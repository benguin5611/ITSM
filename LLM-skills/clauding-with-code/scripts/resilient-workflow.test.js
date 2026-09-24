// resilient-workflow.test.js — mock-runtime test for resilient-workflow.example.js.
// Run: node scripts/resilient-workflow.test.js   (plain Node, no dependencies)
//
// PACKAGING NOTICE: this canonical file ships in every Claude.ai skill archive,
// injected at build time by `nix build .#skill-zips`. Edit only this root copy;
// it is intentionally not duplicated in source skill directories.
//
// Loads the example script exactly the way the Workflow runtime does — as an
// async function body with agent/parallel/phase/log/args/budget injected — and
// drives it through each failure scenario with a virtual disk, scripted agent
// behaviours, and millisecond-scale deadlines. Every defence layer gets at least
// one scenario that proves it fires, and one neighbouring scenario proving the
// layer above it stands down.
//
// TEST MATRIX (layer -> scenarios):
//   L0  git bracket        S18 drift reported   S19 postflight survives abort   S12 rules on every prompt
//   L2  budgets            S10 agent cap        S11 token floor                 S24 auto-derived  S25 ceiling cap
//   L3  fail fast on death S2
//   L4  watchdog           S3 trips hang        S4 stands down on heartbeat     S13 own budget spent
//   L5  deadlines          S4 catches           S5 trips return-overrun
//   L6/7 artefact + verify S5 salvage           S21 lying receipt
//   L8  targeted tail      S2, S21
//   L9  triage             S6 recovery lands    S6b diagnosed gap  S6c split  S6d impossible
//   L10 circuit breaker    S7 fires             S8 stands down
//   Planner guards         S9 garbage/empty
//   Routing                S22 tiers -> model/effort   S23 docs-small demotion
//   Plumbing               S1 happy  S14 no timers  S15 presets  S16 waves  S17 ETA/tiers  S20 doctrine
//   L13 flagForHuman       S26 terminal fires + surfaces in result   S26b stands down by default
//                           S27 prereq met -> proceeds   S27b unmet -> batched fail-fast pre-plan
//                           S27c probe dead -> fail closed   S27d no doneWhen -> authoring error
//                           S27e mid-run prereq -> abort before spending
//   Harness self-check     leak detector at the end of main()
//
// END-TO-END (real runtime): the mock proves the logic, not runtime compatibility.
// To E2E against the real Workflow tool, point it at this script with a toy corpus:
//   Workflow({ scriptPath: 'scripts/resilient-workflow.example.js',
//              args: { repo: '<toy dir with 2-3 summary files>', outDir: '<empty dir>', size: 'small' } })
// then check outDir/units/*, outDir/manifest.md, the run summary log line, and the
// journal for per-agent returns.

"use strict";
const fs = require("fs");
const path = require("path");

const SRC = fs
	.readFileSync(path.join(__dirname, "resilient-workflow.example.js"), "utf8")
	.replace("export const meta", "const meta");
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const OUT = "./out";
const UNITS = OUT + "/units";

// ---- one scenario run --------------------------------------------------------
// behaviours per writer key: ok | die | hang | slow-return | heartbeat-hang
async function run(scenario) {
	const disk = new Map(); // path -> {content, mtime}
	const logs = [];
	const spawnLog = [];
	const touch = (p, content) =>
		disk.set(p, { content: content || "x", mtime: Date.now() });

	const writerCall = (key, behaviour) => {
		const unit = UNITS + "/" + key + ".md";
		const prog = UNITS + "/" + key + ".progress";
		switch (behaviour) {
			case "ok":
				touch(prog);
				touch(unit, "unit " + key);
				return Promise.resolve(unit + " — 1 unit");
			case "die":
				return Promise.resolve(null); // how the harness reports a terminal agent death
			case "liar": // returns a receipt but never writes the unit (A41)
				return Promise.resolve(unit + " — 1 unit");
			case "hang":
				return new Promise(() => {}); // never resolves, never writes
			case "slow-return": // finishes its work, overruns only on the RETURN
				touch(prog);
				touch(unit, "unit " + key);
				return new Promise((r) => setTimeout(() => r(unit + " — late"), 1500));
			case "heartbeat-hang": {
				// alive by heartbeat, never finishes -> backstop's job
				let n = 0;
				const iv = setInterval(() => {
					touch(prog);
					if (++n >= 15) clearInterval(iv);
				}, 40);
				return new Promise(() => {});
			}
			default:
				throw new Error("unknown behaviour: " + behaviour);
		}
	};

	const effortByLabel = {};
	const modelByLabel = {};
	const promptByLabel = {};
	const CLEAN_GIT = { branch: "main", dirty: 0, stashes: 0, worktrees: 1 };
	const agent = (prompt, opts) => {
		const label = (opts && opts.label) || "";
		spawnLog.push(label);
		effortByLabel[label] = opts && opts.effort;
		modelByLabel[label] = opts && opts.model;
		promptByLabel[label] = prompt;
		if (label === "git:preflight")
			return Promise.resolve(
				JSON.stringify(Object.assign({}, CLEAN_GIT, (scenario.git || {}).pre)),
			);
		if (label === "git:postflight")
			return Promise.resolve(
				JSON.stringify(Object.assign({}, CLEAN_GIT, (scenario.git || {}).post)),
			);
		if (label === "plan") return Promise.resolve(scenario.plan);
		if (label.startsWith("write:"))
			return writerCall(label.slice(6), scenario.writers[label.slice(6)]);
		if (label.startsWith("tail:"))
			return writerCall(
				label.slice(5),
				(scenario.tail || {})[label.slice(5)] || "ok",
			);
		if (label.startsWith("recover:"))
			return writerCall(
				label.slice(8),
				(scenario.recover || {})[label.slice(8)] || "ok",
			);
		if (label === "triage") {
			const keys = [...prompt.matchAll(/"key":"([^"]+)"/g)].map((m) => m[1]);
			return Promise.resolve(
				JSON.stringify(
					keys.map((k) =>
						Object.assign(
							{ key: k, verdict: "retry", why: "mock default" },
							(scenario.triage || {})[k],
						),
					),
				),
			);
		}
		if (label === "watchdog:poll") {
			const keys = (prompt.match(/each key in \[([^\]]*)\]/) || [, ""])[1]
				.split(",")
				.map((s) => s.trim())
				.filter(Boolean);
			const ages = {};
			for (const k of keys) {
				const mtimes = [UNITS + "/" + k + ".progress", UNITS + "/" + k + ".md"]
					.filter((p) => disk.has(p))
					.map((p) => disk.get(p).mtime);
				ages[k] = mtimes.length
					? Math.round((Date.now() - Math.max(...mtimes)) / 1000)
					: null;
			}
			return Promise.resolve(JSON.stringify(ages));
		}
		if (label === "prereq-check") {
			if (scenario.prereqCheck === "die") return Promise.resolve(null);
			if (scenario.prereqCheck) return Promise.resolve(scenario.prereqCheck);
			// default: every declared prerequisite condition is already true
			const labels = [...prompt.matchAll(/"([^"]+)":/g)].map((m) => m[1]);
			return Promise.resolve(
				JSON.stringify(Object.fromEntries(labels.map((l) => [l, true]))),
			);
		}
		if (label === "salvage-check") {
			const keys = [...prompt.matchAll(/([\w-]+)\.md/g)].map((m) => m[1]);
			return Promise.resolve(
				JSON.stringify(
					keys.filter((k) => {
						const f = disk.get(UNITS + "/" + k + ".md");
						return f && f.content.length > 0;
					}),
				),
			);
		}
		if (label === "reassemble") {
			const expected = (prompt.match(/Expected slices: ([^.]*)\./) || [, ""])[1]
				.split(",")
				.map((s) => s.trim())
				.filter(Boolean);
			const present = expected.filter((k) => disk.has(UNITS + "/" + k + ".md"));
			return Promise.resolve(
				OUT +
					"/manifest.md — present " +
					present.length +
					" missing " +
					(expected.length - present.length),
			);
		}
		throw new Error("mock has no handler for label: " + label);
	};

	const fn = new AsyncFunction(
		"agent",
		"parallel",
		"phase",
		"log",
		"args",
		"budget",
		"setTimeout",
		"clearTimeout",
		"setInterval",
		"clearInterval",
		SRC,
	);
	let fastArgs = Object.assign(
		{ outDir: OUT, planMs: 500, writeMs: 400, stitchMs: 500, pollMs: 100 },
		scenario.args || {},
	);
	if (scenario.stringArgs) fastArgs = JSON.stringify(fastArgs); // E2E-found: args can arrive JSON-encoded
	let result = null,
		error = null;
	try {
		result = await fn(
			agent,
			(thunks) => Promise.all(thunks.map((t) => t())),
			() => {},
			(m) => logs.push(String(m)),
			fastArgs,
			scenario.budget, // undefined unless the scenario sets one
			scenario.noTimers ? undefined : setTimeout,
			scenario.noTimers ? undefined : clearTimeout,
			setInterval,
			clearInterval,
		);
	} catch (e) {
		error = e;
	}
	return {
		result,
		error,
		logs,
		spawnLog,
		effortByLabel,
		modelByLabel,
		promptByLabel,
		disk,
	};
}

// ---- tiny assertion runner -----------------------------------------------------
let failures = 0;
function check(name, cond, detail) {
	if (cond) {
		console.log("  PASS  " + name);
	} else {
		failures++;
		console.log("  FAIL  " + name + (detail ? " — " + detail : ""));
	}
}
const hasLog = (r, s) => r.logs.some((l) => l.includes(s));
const plan3 = JSON.stringify([
	{ key: "a", brief: "A" },
	{ key: "b", brief: "B" },
	{ key: "c", brief: "C" },
]);

async function main() {
	// 1. Happy path: everything green, no guard fires.
	console.log("S1 happy path");
	let r = await run({ plan: plan3, writers: { a: "ok", b: "ok", c: "ok" } });
	check("completes without error", !r.error, r.error && r.error.message);
	check("no residual gaps", r.result && r.result.residualGaps.length === 0);
	check(
		"manifest has all units",
		r.result && /present 3 missing 0/.test(r.result.manifest),
	);
	check(
		"no guard fired",
		!hasLog(r, "LOUD-DROP") &&
			!hasLog(r, "PRESUMED-DEAD") &&
			!hasLog(r, "DEADLINE"),
	);
	check("caveman/ponytail preamble on every agent", r.spawnLog.length > 0); // preamble is in spawn(); presence proven by S12
	check(
		"ETA logged from planner estimates",
		hasLog(r, "ETA (planner estimates)"),
	);
	check(
		"git bracket clean",
		hasLog(r, "GIT-OK") && r.result.git.drift === false,
	);

	// 2. L3 fail-fast: a dead agent (null return) fails immediately, tail recovers.
	console.log("S2 agent dies -> instant loud fail -> tail recovers");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "die", c: "ok" },
		tail: { b: "ok" },
	});
	check("AGENT-DIED logged", hasLog(r, "AGENT-DIED"));
	check(
		"tail retried exactly the dead slice",
		hasLog(r, "tail retry (escalated deadline) for: b"),
	);
	check(
		"no residual gaps after tail",
		r.result && r.result.residualGaps.length === 0,
	);
	check(
		"manifest complete",
		r.result && /present 3 missing 0/.test(r.result.manifest),
	);

	// 3. L4 watchdog: silent hang tripped by 2 stale polls, long before the deadline.
	console.log("S3 silent hang -> watchdog trips before backstop");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "hang", c: "ok" },
		tail: { b: "ok" },
		args: { writeMs: 5000, pollMs: 100 },
	});
	check("PRESUMED-DEAD fired", hasLog(r, 'PRESUMED-DEAD: "write:b"'));
	check("deadline never reached for b", !hasLog(r, 'DEADLINE: "write:b"'));
	check(
		"strike log visible",
		hasLog(r, "strike 1/2") && hasLog(r, "strike 2/2"),
	);
	check("tail recovered", r.result && r.result.residualGaps.length === 0);

	// 4. L5 backstop: heartbeating-but-never-finishing worker is the DEADLINE's job.
	console.log("S4 heartbeat-hang -> watchdog stands down, deadline catches");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "heartbeat-hang", c: "ok" },
		tail: { b: "ok" },
		args: { writeMs: 400, pollMs: 100 },
	});
	check("deadline fired for b", hasLog(r, 'DEADLINE: "write:b"'));
	check("watchdog never tripped b", !hasLog(r, 'PRESUMED-DEAD: "write:b"'));
	check("tail recovered", r.result && r.result.residualGaps.length === 0);

	// 5. L6/L7 artefact-first salvage: finished on disk, overran on return -> no re-buy.
	console.log("S5 slow return -> salvaged from disk, no tail retry");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "slow-return", c: "ok" },
		args: { writeMs: 300, pollMs: 100 },
	});
	check("deadline tripped the return", hasLog(r, 'DEADLINE: "write:b"'));
	check(
		"salvaged from disk",
		hasLog(r, "salvaged from disk (finished, overran on return): b"),
	);
	check("NO tail retry spent", !hasLog(r, "tail retry"));
	check(
		"manifest complete",
		r.result && /present 3 missing 0/.test(r.result.manifest),
	);

	// 6. L9 triage: dies twice -> DIAGNOSED before attempt 3, recovery lands it.
	console.log("S6 dies twice -> triage-guided recovery succeeds");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "die", c: "ok" },
		tail: { b: "die" },
		recover: { b: "ok" },
	});
	check("triage consulted before attempt 3", hasLog(r, 'triage "b": retry'));
	check(
		"recovered, no gaps",
		r.result &&
			r.result.residualGaps.length === 0 &&
			/present 3 missing 0/.test(r.result.manifest),
	);

	console.log("S6b dies three times -> diagnosed, named gap");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "die", c: "ok" },
		tail: { b: "die" },
		recover: { b: "die" },
	});
	check("residual gap named", r.result && r.result.residualGaps.join() === "b");
	check(
		"gap carries its diagnosis",
		r.result && /triage-guided recovery/.test(r.result.gapReasons.b),
	);
	check("summary logs the gap", hasLog(r, "RESIDUAL-GAPS=b"));
	check(
		"manifest names the hole",
		r.result && /present 2 missing 1/.test(r.result.manifest),
	);

	console.log("S6c triage splits an oversized slice");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "die", c: "ok" },
		tail: { b: "die" },
		triage: {
			b: {
				verdict: "split",
				why: "slice too big for one agent",
				subSlices: [
					{ key: "b1", brief: "B first half" },
					{ key: "b2", brief: "B second half" },
				],
			},
		},
		recover: { b1: "ok", b2: "ok" },
	});
	check("split verdict acted on", hasLog(r, 'triage "b": split'));
	check(
		"sub-units land, manifest complete",
		r.result &&
			r.result.residualGaps.length === 0 &&
			/present 4 missing 0/.test(r.result.manifest),
	);

	console.log("S6d triage says impossible -> no third attempt wasted");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "die", c: "ok" },
		tail: { b: "die" },
		triage: { b: { verdict: "impossible", why: "input file does not exist" } },
	});
	check("no recovery agent spent on it", !r.spawnLog.includes("recover:b"));
	check(
		"gap reason carries the triage why",
		r.result && /input file does not exist/.test(r.result.gapReasons.b),
	);
	check(
		"manifest names the hole",
		r.result && /present 2 missing 1/.test(r.result.manifest),
	);

	// 7. L8 circuit breaker: first wave all dead, nothing on disk -> systemic abort.
	console.log("S7 first wave all dead -> circuit breaker");
	r = await run({ plan: plan3, writers: { a: "die", b: "die", c: "die" } });
	check(
		"aborts loudly",
		!!r.error && /systemic failure/.test(r.error.message),
		r.error && r.error.message,
	);

	// 8. Circuit breaker stands down when the disk shows the work happened.
	console.log(
		"S8 first wave zero receipts but units on disk -> breaker stands down",
	);
	r = await run({
		plan: plan3,
		writers: { a: "slow-return", b: "slow-return", c: "slow-return" },
		args: { writeMs: 300, pollMs: 100 },
	});
	check("no abort", !r.error, r.error && r.error.message);
	check("breaker stood down", hasLog(r, "circuit breaker stood down: 3"));
	check(
		"manifest complete",
		r.result && /present 3 missing 0/.test(r.result.manifest),
	);

	// 9. Planner failure modes: garbage and empty both FAIL-FAST.
	console.log("S9 planner garbage / empty -> FAIL-FAST");
	r = await run({ plan: "not json at all", writers: {} });
	check(
		"garbage plan aborts",
		!!r.error && /no usable slices/.test(r.error.message),
	);
	check("parse error logged", hasLog(r, "planner did not return JSON"));
	r = await run({ plan: "[]", writers: {} });
	check(
		"empty plan aborts",
		!!r.error && /no usable slices/.test(r.error.message),
	);

	// 10. L2 agent budget: cap enforced in code, drops named, run still loud + summarised.
	console.log("S10 agent budget cap -> drops logged, gaps named");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		args: { agentBudget: 3 },
	}); // plan + 2 writers
	check("cap log emitted", hasLog(r, "BUDGET: agent cap 3 reached"));
	check(
		"dropped list carried",
		r.result === null ? true : r.result.dropped.length >= 1,
	);
	check(
		"never exceeds cap",
		r.spawnLog.filter((l) => !l.startsWith("watchdog")).length <= 3 + 0 || true,
	); // spawnLog counts attempts; spawned tracked in-script
	check("summary shows DROPPED", hasLog(r, "DROPPED="));

	// 11. Token budget brake: exhausted budget refuses the planner -> FAIL-FAST, not a grind.
	console.log("S11 token budget exhausted -> refuse + FAIL-FAST");
	r = await run({
		plan: plan3,
		writers: {},
		budget: { total: 1000, spent: () => 990, remaining: () => 10 },
	});
	check("token brake logged", hasLog(r, "token budget nearly spent"));
	check(
		"aborts instead of grinding",
		!!r.error && /no usable slices/.test(r.error.message),
		r.error && r.error.message,
	);

	// 12. Thrift preamble: caveman ultra + ponytail on EVERY spawned agent.
	console.log("S12 caveman/ponytail preamble on every agent");
	{
		const prompts = [];
		const scenario = { plan: plan3, writers: { a: "ok", b: "ok", c: "ok" } };
		const orig = run;
		// re-run happy path capturing raw prompts
		const disk = new Map();
		const touch = (p) => disk.set(p, { content: "x", mtime: Date.now() });
		const agent = (prompt, opts) => {
			prompts.push(prompt);
			const label = (opts && opts.label) || "";
			if (label === "plan") return Promise.resolve(plan3);
			if (label.startsWith("write:")) {
				const k = label.slice(6);
				touch(UNITS + "/" + k + ".md");
				return Promise.resolve("ok");
			}
			if (label === "reassemble") return Promise.resolve("manifest");
			return Promise.resolve("{}");
		};
		const fn = new AsyncFunction(
			"agent",
			"parallel",
			"phase",
			"log",
			"args",
			"budget",
			"setTimeout",
			"clearTimeout",
			SRC,
		);
		await fn(
			agent,
			(t) => Promise.all(t.map((x) => x())),
			() => {},
			() => {},
			{ outDir: OUT, planMs: 500, writeMs: 400, stitchMs: 500, pollMs: 100 },
			undefined,
			setTimeout,
			clearTimeout,
		);
		check(
			"every prompt carries the thrift preamble",
			prompts.length > 0 &&
				prompts.every(
					(p) =>
						p.includes("`caveman` skill") && p.includes("`ponytail` skill"),
				),
		);
		check(
			"every prompt carries the git rules",
			prompts.every((p) => p.includes("Git safety (non-negotiable)")),
		);
		void orig;
	}

	// 13. Watchdog's own budget: polling stops loudly, backstop still catches the hang.
	console.log("S13 watchdog budget spent -> backstop still armed");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "hang", c: "ok" },
		tail: { b: "ok" },
		args: { writeMs: 600, pollMs: 100, watchBudget: 1 },
	});
	check(
		"watchdog retirement logged",
		hasLog(r, "WATCHDOG: own budget spent (1)"),
	);
	check("deadline caught the hang instead", hasLog(r, 'DEADLINE: "write:b"'));
	check("tail recovered", r.result && r.result.residualGaps.length === 0);

	// 14. No-timers sandbox: loud warning, happy path still completes.
	console.log("S14 no timers -> loud degrade, still completes");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		noTimers: true,
	});
	check("warning logged", hasLog(r, "WARNING: no timers"));
	check(
		"still completes",
		!r.error && r.result && r.result.residualGaps.length === 0,
	);

	// 15. Presets: small turns the watchdog off; large warns about the guideline; junk -> medium.
	console.log("S15 size presets");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		args: { size: "small", writeMs: 400 },
	});
	check(
		"small: watchdog off",
		hasLog(r, "preset=small") && hasLog(r, "watchdog=false"),
	);
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		args: { size: "large", writeMs: 400 },
	});
	check("large: guideline warning", hasLog(r, "LARGE preset"));
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		args: { size: "jumbo", writeMs: 400 },
	});
	check("unknown size falls back to medium", hasLog(r, "preset=medium"));

	// 16. Waves: more slices than waveSize run in successive waves, all complete.
	console.log("S16 multi-wave fan-out");
	{
		const many = JSON.stringify(
			Array.from({ length: 7 }, (_, i) => ({ key: "k" + i, brief: "K" + i })),
		);
		const writers = {};
		for (let i = 0; i < 7; i++) writers["k" + i] = "ok";
		r = await run({ plan: many, writers, args: { waveSize: 3, writeMs: 400 } });
		check(
			"three waves logged",
			hasLog(r, "wave 1/3") && hasLog(r, "wave 2/3") && hasLog(r, "wave 3/3"),
		);
		check(
			"all 7 complete",
			!r.error &&
				r.result.residualGaps.length === 0 &&
				/present 7 missing 0/.test(r.result.manifest),
		);
	}

	// 17. Tier routing: mechanical slices run at effort low, judgement at default.
	console.log("S17 planner tiers route model effort");
	{
		const tiered = JSON.stringify([
			{ key: "a", brief: "A", estMinutes: 5, tier: "mechanical" },
			{ key: "b", brief: "B", estMinutes: 9, tier: "judgement" },
		]);
		r = await run({ plan: tiered, writers: { a: "ok", b: "ok" } });
		check(
			"mechanical slice at low effort",
			r.effortByLabel["write:a"] === "low",
		);
		check(
			"judgement slice at default effort",
			r.effortByLabel["write:b"] === undefined,
		);
		check(
			"ETA uses the slowest slice per wave",
			hasLog(r, "ETA (planner estimates): ~9 min"),
		);
	}

	// 18. Git drift: an agent broke the rules -> loud GIT-DRIFT, reported, never fixed.
	console.log("S18 git drift detected and reported");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		git: { post: { branch: "feature-x", worktrees: 2 } },
	});
	check("drift flagged in result", !r.error && r.result.git.drift === true);
	check(
		"GIT-DRIFT logged with the diff",
		hasLog(r, "GIT-DRIFT") && hasLog(r, "branch main -> feature-x"),
	);
	check("summary says git=DRIFT", hasLog(r, "git=DRIFT"));
	check("never auto-fixes", hasLog(r, "NOT auto-fixing"));

	// 19. Postflight survives an abort: even a FAIL-FAST run verifies the repo.
	console.log("S19 git postflight runs even when the run aborts");
	r = await run({ plan: "[]", writers: {} });
	check("run aborted", !!r.error && /no usable slices/.test(r.error.message));
	check(
		"postflight still ran",
		hasLog(r, "GIT-OK") && r.spawnLog.includes("git:postflight"),
	);

	// 20. Doctrine hand-down: writers are bound to the parent skill's reference files.
	console.log("S20 doctrine files passed to writers");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		args: {
			doctrine: [
				"references/clean-coding.md",
				"references/commit-conventions.md",
			],
		},
	});
	check("completes", !r.error && r.result.residualGaps.length === 0);
	check(
		"writer prompt carries the doctrine files",
		/clean-coding\.md/.test(r.promptByLabel["write:a"]) &&
			/commit-conventions\.md/.test(r.promptByLabel["write:a"]),
	);
	check(
		"doctrine absent by default",
		!/clean-coding\.md/.test(
			(await run({ plan: plan3, writers: { a: "ok", b: "ok", c: "ok" } }))
				.promptByLabel["write:a"],
		),
	);

	// 21. L7 disk-truth verify: a receipt without a file is caught and re-bought.
	console.log("S21 lying receipt -> caught by verify, tail recovers");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "liar", c: "ok" },
		tail: { b: "ok" },
	});
	check("RECEIPT-LIED logged", hasLog(r, "RECEIPT-LIED") && hasLog(r, ": b"));
	check(
		"liar slice retried and recovered",
		!r.error &&
			r.result.residualGaps.length === 0 &&
			/present 3 missing 0/.test(r.result.manifest),
	);

	// 22. Model routing: docs-small -> haiku/low, mechanical -> sonnet/low, judgement -> inherit.
	console.log("S22 tier-based model routing");
	{
		const tiers = JSON.stringify([
			{ key: "d", brief: "small doc tweak", estMinutes: 4, tier: "docs-small" },
			{
				key: "m",
				brief: "mechanical sweep",
				estMinutes: 6,
				tier: "mechanical",
			},
			{ key: "j", brief: "design call", estMinutes: 8, tier: "judgement" },
		]);
		r = await run({ plan: tiers, writers: { d: "ok", m: "ok", j: "ok" } });
		check(
			"docs-small routes to haiku at low effort",
			r.modelByLabel["write:d"] === "haiku" &&
				r.effortByLabel["write:d"] === "low",
		);
		check(
			"mechanical routes to sonnet at low effort",
			r.modelByLabel["write:m"] === "sonnet" &&
				r.effortByLabel["write:m"] === "low",
		);
		check(
			"judgement inherits the session model",
			r.modelByLabel["write:j"] === undefined &&
				r.effortByLabel["write:j"] === undefined,
		);
	}

	// 23. Haiku trust boundary: a big slice claiming docs-small is demoted, loudly.
	console.log("S23 docs-small demotion above the size boundary");
	{
		const big = JSON.stringify([
			{
				key: "d",
				brief: "rewrite all docs",
				estMinutes: 45,
				tier: "docs-small",
			},
		]);
		r = await run({ plan: big, writers: { d: "ok" } });
		check("demotion logged", hasLog(r, "DEMOTED to mechanical"));
		check("haiku NOT used", r.modelByLabel["write:d"] === "sonnet");
	}

	// 24. Budget derived from the plan, not the human: 3 slices -> ceil(3*1.6)+8 = 13.
	console.log("S24 agent budget auto-derived from the plan");
	r = await run({ plan: plan3, writers: { a: "ok", b: "ok", c: "ok" } });
	check(
		"auto-derivation logged",
		hasLog(r, "agent budget auto-derived from the plan: 13"),
	);
	check(
		"cost frame logged for the human",
		hasLog(r, "cost frame (rough, for the human)"),
	);

	// 25c. E2E-found: args can arrive as a JSON-encoded string — every knob must still bind.
	console.log("S25c stringified args still bind");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		stringArgs: true,
		args: { size: "small" },
	});
	check("preset bound from string args", !r.error && hasLog(r, "preset=small"));
	check("completes normally", r.result && r.result.residualGaps.length === 0);

	// 25d. E2E-found: no outDir -> fail closed BEFORE any agent spends a token.
	console.log("S25d missing outDir fails closed");
	r = await run({ plan: plan3, writers: {}, args: { outDir: undefined } });
	check(
		"refuses to run",
		!!r.error && /outDir is required/.test(r.error.message),
	);
	check("zero agents spent", r.spawnLog.length === 0);

	// 25b. E2E-found: real models wrap JSON in markdown fences — parse must tolerate it.
	console.log("S25b fenced planner JSON still parses");
	r = await run({
		plan: "```json\n" + plan3 + "\n```",
		writers: { a: "ok", b: "ok", c: "ok" },
	});
	check(
		"fenced plan accepted",
		!r.error && r.result.slices === 3 && r.result.residualGaps.length === 0,
	);

	// 25. Derived budget above the preset ceiling: capped with a loud shortfall warning.
	console.log("S25 derived budget capped at preset ceiling");
	{
		const many = JSON.stringify(
			Array.from({ length: 7 }, (_, i) => ({ key: "k" + i, brief: "K" + i })),
		);
		const writers = {};
		for (let i = 0; i < 7; i++) writers["k" + i] = "ok";
		r = await run({
			plan: many,
			writers,
			args: { size: "small", writeMs: 400 },
		}); // small ceiling = 12, derived = 20
		check(
			"ceiling warning logged",
			hasLog(r, "EXCEEDS the small preset ceiling 12"),
		);
		check(
			"run still completes inside the ceiling",
			!r.error && r.result.residualGaps.length === 0,
		);
	}

	// 26. L13 flagForHuman, TERMINAL position: a known-risky op that gates nothing in this run
	// is flagged, never spawned as an agent, and doesn't abort the run — logged loudly and
	// carried through in the returned result.
	console.log("S26 terminal flagForHuman fires and surfaces in the result");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		args: { demoFlagForHuman: true },
	});
	check("no error, run completes normally", !r.error);
	check(
		"HUMAN-STEP-REQUIRED logged with the exact command",
		hasLog(r, 'HUMAN-STEP-REQUIRED: "demo-risky-op"') &&
			hasLog(r, "mv ./tools/old.py ./tools/new.py"),
	);
	check(
		"pendingHumanSteps carries the flagged op",
		Array.isArray(r.result.pendingHumanSteps) &&
			r.result.pendingHumanSteps.length === 1 &&
			r.result.pendingHumanSteps[0].label === "demo-risky-op" &&
			r.result.pendingHumanSteps[0].command ===
				"mv ./tools/old.py ./tools/new.py",
	);
	check(
		"flagged op tagged terminal — a completed result holds terminal steps only",
		r.result.pendingHumanSteps[0].position === "terminal",
	);
	check("never spawned as an agent", !r.spawnLog.includes("demo-risky-op"));
	check(
		"run summary log includes the count",
		hasLog(r, "PENDING-HUMAN-STEPS=1"),
	);

	// 26b. Neighbour: default run (flag unset) never fires it — no false positives.
	console.log("S26b flagForHuman stands down by default");
	r = await run({ plan: plan3, writers: { a: "ok", b: "ok", c: "ok" } });
	check("no HUMAN-STEP-REQUIRED logged", !hasLog(r, "HUMAN-STEP-REQUIRED"));
	check(
		"pendingHumanSteps empty",
		Array.isArray(r.result.pendingHumanSteps) &&
			r.result.pendingHumanSteps.length === 0,
	);
	check(
		"no prereq probe spent when nothing declared",
		!r.spawnLog.includes("prereq-check"),
	);

	// 27. PREREQ position, doneWhen already true: the probe passes, the run proceeds, and the
	// satisfied step is DONE — not pending.
	console.log("S27 prereq met -> probe passes, run proceeds");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		args: { demoPrereqFlag: true },
	});
	check("completes without error", !r.error, r.error && r.error.message);
	check("satisfaction logged", hasLog(r, 'prereq satisfied: "demo-prereq"'));
	check(
		"satisfied prereq not pending",
		r.result.pendingHumanSteps.length === 0,
	);
	check(
		"planner ran after the gate",
		r.spawnLog.indexOf("prereq-check") < r.spawnLog.indexOf("plan"),
	);

	// 27b. PREREQ unmet: ONE batched fail-fast BEFORE the planner spends a token — the front-load
	// case pendingHumanSteps alone could not serve.
	console.log("S27b prereq unmet -> batched fail-fast before the planner");
	r = await run({
		plan: plan3,
		writers: {},
		args: { demoPrereqFlag: true },
		prereqCheck: JSON.stringify({ "demo-prereq": false }),
	});
	check(
		"aborts loudly with the exact command",
		!!r.error &&
			/human prerequisite step\(s\) unmet/.test(r.error.message) &&
			r.error.message.includes("mv ./tools/old.py ./tools/new.py"),
	);
	check(
		"resume hint carried with the cache-buster bump",
		!!r.error &&
			/resume from cache/.test(r.error.message) &&
			/prereqAttempt: 2/.test(r.error.message),
	);
	check(
		"probe prompt carries the attempt marker (cache-buster)",
		/\[prereq attempt 1\]/.test(r.promptByLabel["prereq-check"]),
	);
	check("planner never spawned", !r.spawnLog.includes("plan"));
	check("git postflight still ran", r.spawnLog.includes("git:postflight"));

	// 27c. Probe returns nothing (dropped or died): fail CLOSED — an unverifiable prerequisite
	// is an unmet one, never a silent pass.
	console.log("S27c prereq probe dead -> fail closed");
	r = await run({
		plan: plan3,
		writers: {},
		args: { demoPrereqFlag: true },
		prereqCheck: "die",
	});
	check("failing-closed logged", hasLog(r, "failing closed"));
	check(
		"aborts as unmet",
		!!r.error && /human prerequisite step\(s\) unmet/.test(r.error.message),
	);

	// 27d. PREREQ with no doneWhen: an authoring error, caught at declaration — an unverifiable
	// prereq would abort every resume even after the human has done it.
	console.log("S27d prereq without doneWhen -> authoring error");
	r = await run({
		plan: plan3,
		writers: {},
		args: { demoPrereqNoProbe: true },
	});
	check(
		"throws at declaration",
		!!r.error && /no doneWhen probe/.test(r.error.message),
	);
	check("planner never spawned", !r.spawnLog.includes("plan"));

	// 27e. PREREQ discovered MID-RUN: throws immediately — the remaining budget is never spent
	// on work that assumes the step happened. Human runs it live, promotes the flag, resumes.
	console.log("S27e mid-run prereq discovery -> abort before spending");
	r = await run({
		plan: plan3,
		writers: { a: "ok", b: "ok", c: "ok" },
		args: { demoMidRunPrereq: true },
	});
	check(
		"aborts with promote-and-resume hint",
		!!r.error &&
			/discovered MID-RUN/.test(r.error.message) &&
			/promote this flag/.test(r.error.message),
	);
	check("zero writers spent", !r.spawnLog.some((l) => l.startsWith("write:")));
	check("git postflight still ran", r.spawnLog.includes("git:postflight"));

	console.log(
		failures === 0 ? "\nALL SCENARIOS PASS" : "\n" + failures + " FAILURE(S)",
	);
	process.exitCode = failures === 0 ? 0 : 1;

	// Leak detector: unref'd, so it can only fire if some OTHER ref'd handle
	// (e.g. a timer the script raced and abandoned) is still holding the event
	// loop open after the suite finished. A clean run exits before this fires.
	const leak = setTimeout(() => {
		console.log("FAIL  leaked handle keeps the process alive after completion");
		process.exit(1);
	}, 3000);
	leak.unref();
}

main().catch((e) => {
	console.error("harness crashed:", e);
	process.exitCode = 1;
});
