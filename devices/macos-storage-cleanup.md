# Identifying and reducing large storage usage on macOS

This guide explains how to diagnose high disk usage on macOS and reclaim space safely. It is written for modern APFS-based macOS systems, with an emphasis on developer workstations.

---

## Table of Contents

1. [How much space do you have?](#1-how-much-space-do-you-have)
2. [Find what's using your disk space](#2-find-whats-using-your-disk-space)
3. [Where your files actually live](#3-where-your-files-actually-live-macos-volume-structure)
4. [What to clean first (priority order)](#4-what-to-clean-first-priority-order)
5. [What to expect after cleaning up](#5-what-to-expect-after-cleaning-up)
6. [Developer storage (often 50-200+ GB)](#6-developer-storage-often-50-200-gb)
   - [6.0 Automated cleanup tools](#60-automated-cleanup-tools)
   - [6.1 Language and build tool caches](#61-language-and-build-tool-caches)
   - [6.2 Build artefacts and dependencies](#62-build-artefacts-and-dependencies)
   - [6.3 Package managers and system-level dev stores](#63-package-managers-and-system-level-dev-stores)
   - [6.4 IDE caches and extensions](#64-ide-caches-and-extensions)
7. [User application caches](#7-user-application-caches)
8. [System data and local backups](#8-system-data-and-local-backups)
   - [8.1 Old software updates](#81-old-software-updates)
   - [8.2 System-level caches](#82-system-level-caches)
   - [8.3 System logs](#83-system-logs)
9. [Old macOS system data (Previous System)](#9-old-macos-system-data-previous-system)

---

## 1. How much space do you have?

**Identify:**
```bash
df -h /
```

If free space is below 15 percent, expect performance issues on Apple Silicon devices.

**Safe free-space thresholds for Apple Silicon SSDs:**
- Ideal: ~20% free
- Minimum safe: ~15% free
- Degradation zone: <10% free
- High wear / heavy swap: <5% free

## 2. Find what's using your disk space

**Identify:**
```bash
sudo du -sh /* 2>/dev/null | sort -h
```

Focus on: `/Users`, `/Applications`, `/Library`, `/private`, `/opt`, `/nix`.

Then inspect the writable data volume:
```bash
sudo du -xhd1 /System/Volumes/Data 2>/dev/null | sort -h
```

Example output:
```
  0B	/System/Volumes/Data/cores
  0B	/System/Volumes/Data/home
  0B	/System/Volumes/Data/mnt
  0B	/System/Volumes/Data/sw
  0B	/System/Volumes/Data/Volumes
192K	/System/Volumes/Data/.fseventsd
2.3M	/System/Volumes/Data/MobileSoftwareUpdate
3.2M	/System/Volumes/Data/.PreviousSystemInformation
 98M	/System/Volumes/Data/usr
5.5G	/System/Volumes/Data/System
5.9G	/System/Volumes/Data/opt
6.1G	/System/Volumes/Data/Library
 12G	/System/Volumes/Data/private
 15G	/System/Volumes/Data/Applications
 45G	/System/Volumes/Data/Users
 89G	/System/Volumes/Data
```

This shows where your real storage consumption is located.

## 3. Where your files actually live (macOS volume structure)

Modern macOS splits the root APFS container into:
- A sealed, read-only system volume
- A writable data volume mounted at `/System/Volumes/Data`

User and application growth lives on `/System/Volumes/Data`, so when drilling down by directory (e.g., with `du`), focus there.

## 4. What to clean first (priority order)

When low on space, prioritise in this order:

1. **Trash and Downloads** (safest, highest visibility) → Manual cleanup
2. **Old installers and disk images** (`*.dmg`, `*.pkg`, archives) → Manual cleanup
3. **Developer build artefacts** (node_modules, __pycache__) → See [§6.2](#62-build-artefacts-and-dependencies)
4. **Docker / Homebrew / Nix / language tool caches** → See [§6.3](#63-package-managers-and-system-level-dev-stores)
5. **IDE caches** (VS Code, JetBrains) → See [§6.4](#64-ide-caches-and-extensions)
6. **Browser and application caches** → See [§7](#7-user-application-caches), [§8.2](#82-system-level-caches)
7. **Previous System** (removes rollback capability) → See [§9](#9-old-macos-system-data-previous-system)

**⚠️ Important:** Read the warnings in each section before running commands.

---

## 5. What to expect after cleaning up

After clearing caches, expect:
- Slower first launch for some applications
- Rebuild of indexes (Mail, Spotlight)
- Re-download of cached content (browsers, package managers)

**Restart affected applications after cleanup.**

---

## 6. Developer storage (often 50-200+ GB)

### 6.0 Automated cleanup tools

[Mole](https://github.com/tw93/mole) is a CLI binary that scans for large cache and junk directories across package managers, IDEs, and applications. It covers many of the categories in this guide and is a good starting point before manual per-tool cleanup.

**Install:**
```bash
brew install mole
```

Use Mole for a quick first pass, then follow the sections below for package managers or caches it does not cover.

---

### 6.1 Language and build tool caches

#### 6.1.1 Node.js (npm, pnpm, yarn)

**Identify:**
```bash
du -sh ~/.npm ~/.yarn 2>/dev/null

# pnpm store size
pnpm store path 2>/dev/null | xargs -I{} du -sh "{}" 2>/dev/null
```

**Clean:**
```bash
# npm - cache only (safe)
npm cache clean --force

# pnpm - removes unreferenced packages from store (safe)
pnpm store prune

# WARNING: Advanced - deletes the entire npm cache and state under ~/.npm
# npm will re-download packages and may need to rebuild metadata
# Only uncomment if you want a completely clean npm cache/state
# rm -rf ~/.npm

# WARNING: Advanced - deletes ALL Yarn global packages and state
# You'll need to reinstall any global Yarn tools
# Only uncomment if you want a completely clean Yarn environment
# rm -rf ~/.yarn
```

#### 6.1.2 Go

**Identify:**
```bash
du -sh ~/Library/Caches/go-build ~/Library/Caches/gopls 2>/dev/null
```

**Clean:**
```bash
# Removes build cache and language server cache (safe, will rebuild)
rm -rf ~/Library/Caches/go-build
rm -rf ~/Library/Caches/gopls
```

#### 6.1.3 Java/Android (Gradle)

**Identify:**
```bash
du -sh ~/.gradle 2>/dev/null
```

**Clean:**
```bash
# Only if not actively doing Android/Java development
# WARNING: Deletes all cached dependencies, requires large re-downloads
# rm -rf ~/.gradle/caches
```

#### 6.1.4 Rust (cargo)

**Identify:**
```bash
du -sh ~/.cargo/registry ~/.cargo/git 2>/dev/null
```

**Clean:**
```bash
# Removes downloaded crate sources and git checkouts (safe - re-downloaded on next build)
rm -rf ~/.cargo/registry/cache
rm -rf ~/.cargo/registry/src
rm -rf ~/.cargo/git/db

# WARNING: Do NOT delete ~/.cargo/bin — that contains installed cargo binaries
```

#### 6.1.5 Maven (Java)

**Identify:**
```bash
du -sh ~/.m2/repository 2>/dev/null
```

**Clean:**
```bash
# WARNING: Deletes all cached Maven dependencies - large re-download required
# Only run if not actively doing Java/Maven development
# rm -rf ~/.m2/repository
```

#### 6.1.6 .NET/NuGet

**Identify:**
```bash
du -sh ~/.nuget/packages ~/.dotnet 2>/dev/null
```

**Clean:**
```bash
# Removes all cached NuGet packages (safe - re-downloaded on next build)
dotnet nuget locals all --clear
```

#### 6.1.7 Haskell (ghcup/cabal/stack)

**Identify:**
```bash
du -sh ~/.ghcup ~/.cabal ~/.stack 2>/dev/null
```

**Clean:**
```bash
# Removes ghcup download cache (safe - reinstall artefacts remain)
ghcup gc --cache

# Removes cabal package index cache (safe - re-downloaded)
rm -rf ~/.cabal/packages

# WARNING: Removes all stack snapshot packages and compilers - large re-download
# rm -rf ~/.stack/snapshots
# rm -rf ~/.stack/programs
```

#### 6.1.8 OCaml (opam)

**Identify:**
```bash
du -sh ~/.opam 2>/dev/null
```

**Clean:**
```bash
# Removes logs, switch backups/build dirs, and repository cache (safe)
opam clean --logs --switch-cleanup --repo-cache
```

#### 6.1.9 C/C++ (Conan)

**Identify:**
```bash
du -sh ~/.conan ~/.conan2 2>/dev/null
```

**Clean:**
```bash
# Removes all cached packages (safe - re-downloaded on next install)
# Conan 2.x:
conan cache clean "*"

# Conan 1.x:
# conan remove "*" --src --builds --force
```

#### 6.1.10 Swift (SwiftPM / CocoaPods)

**Identify:**
```bash
du -sh ~/.swiftpm ~/.cocoapods ~/Library/Caches/CocoaPods 2>/dev/null
```

**Clean:**
```bash
# SwiftPM build cache (safe - rebuilt on next build)
rm -rf ~/Library/Caches/org.swift.swiftpm

# CocoaPods (safe - re-downloaded on next pod install)
pod cache clean --all
```

#### 6.1.11 Scala (sbt / Coursier)

**Identify:**
```bash
du -sh ~/.sbt ~/.ivy2 "$HOME/Library/Application Support/Coursier" 2>/dev/null
```

**Clean:**
```bash
# sbt boot directory (safe - re-downloaded on next sbt launch)
rm -rf ~/.sbt/boot

# WARNING: Removes all ivy/Coursier cached dependencies - large re-download
# rm -rf ~/.ivy2/cache
# rm -rf "$HOME/Library/Application Support/Coursier/cache"
# rm -rf ~/Library/Caches/Coursier
```

#### 6.1.12 Julia

**Identify:**
```bash
du -sh ~/.julia 2>/dev/null
```

**Clean:**
```bash
# Removes unused packages (safe - keeps actively used packages)
julia -e 'using Pkg; Pkg.gc()'

# WARNING: Removes all installed Julia packages - must reinstall per-environment
# rm -rf ~/.julia/packages
```

#### 6.1.13 Kotlin

**Identify:**
```bash
du -sh ~/.kotlin 2>/dev/null
```

**Clean:**
```bash
# Removes Kotlin daemon and script cache (safe - re-created on next use)
rm -rf ~/.kotlin
```

### 6.2 Build artefacts and dependencies

#### 6.2.1 Python bytecode cache

**Identify:**
```bash
find ~ -type d -name "__pycache__" -print0 | xargs -0 du -sh 2>/dev/null | sort -h
```

**Clean:**
```bash
# Removes bytecode cache (safe - auto-regenerated on next run)
find ~ -type d -name "__pycache__" -prune -exec rm -rf {} \;
```

#### 6.2.2 Node.js modules

**Identify:**
```bash
find ~ -maxdepth 6 -type d -name node_modules -prune -print0 | xargs -0 du -sh 2>/dev/null | sort -h
```

**Clean:**
```bash
# SAFEST: Delete node_modules for specific inactive projects manually:
cd ~/path/to/old-project && rm -rf node_modules

# WARNING: Deletes ALL node_modules in your home directory
# Only run this if you want to clean ALL projects (active and inactive)
# You'll need to run npm/pnpm/yarn install in each project afterward
# find ~ -maxdepth 6 -type d -name node_modules -prune -exec rm -rf {} \;
```

---

### 6.3 Package managers and system-level dev stores

#### 6.3.1 Homebrew

**Identify:**
```bash
du -sh /opt/homebrew/Cellar 2>/dev/null
brew cleanup --dry-run
```

**Clean:**
```bash
# Removes old versions of installed packages
brew cleanup

# Removes packages that were installed as dependencies but are no longer needed
brew autoremove
```

#### 6.3.2 Nix

**Identify:**
```bash
du -sh /nix 2>/dev/null
```

**Clean:**
```bash
# WARNING: Removes all unused packages and old generations (reduces ability to roll back)
#Traditional Nix install
sudo /nix/var/nix/profiles/default/bin/nix-collect-garbage -d

#New CLI equivalent (works on recent Nix / Determinate installs)
nix store gc
```

#### 6.3.3 Docker

**Identify:**
```bash
docker system df
```

**Clean:**
```bash
# SAFEST: Selective cleanup
docker container prune  # removes only stopped containers
docker network prune    # removes only unused networks
docker image prune      # removes only dangling images

# WARNING: Removes stopped containers, unused networks, and dangling images
# Review stopped containers first: docker ps -a
# Only run if you're sure stopped containers are disposable
# This destroys any data stored inside stopped containers (unless using volumes)
# docker system prune

# WARNING: Removes ALL unused images, not just dangling ones
# Large re-downloads required; destroys all unpersisted image-only environments
# docker system prune -a
```

#### 6.3.4 pip (PyPI)

**Identify:**
```bash
du -sh ~/Library/Caches/pip 2>/dev/null
```

**Clean:**
```bash
# Removes Python package cache (safe - will re-download)
pip cache purge
```

#### 6.3.5 Terraform

**Identify:**
```bash
du -sh ~/.terraform.d/plugin-cache 2>/dev/null
```

**Clean:**
```bash
# Removes Terraform provider plugin cache (safe - will re-download)
rm -rf ~/.terraform.d/plugin-cache/*
```

#### 6.3.6 Buf

**Identify:**
```bash
du -sh ~/.cache/buf 2>/dev/null
```

**Clean:**
```bash
# Removes Buf module cache (safe - will re-download)
buf registry cc
```

#### 6.3.7 MacPorts

**Identify:**
```bash
du -sh /opt/local 2>/dev/null
sudo port installed inactive 2>/dev/null
```

**Clean:**
```bash
# Removes build files for all installed ports (safe)
sudo port clean --all installed

# Removes inactive (old) port versions (safe - active versions remain)
sudo port -f uninstall inactive
```

#### 6.3.8 Python: pyenv / pipx / Conda

**pyenv (Python versions):**
```bash
# Identify old versions
pyenv versions 2>/dev/null
du -sh ~/.pyenv/versions 2>/dev/null

# Remove a specific old version (safe - active version remains)
# pyenv uninstall <version>
```

**pipx:**
```bash
# Identify
du -sh ~/.local/pipx 2>/dev/null
pipx list 2>/dev/null

# Remove a specific app (safe)
# pipx uninstall <app>

# WARNING: Removes ALL pipx-installed tools
# pipx uninstall-all
```

**Conda / Miniconda / Anaconda / Miniforge:**
```bash
# Identify
du -sh ~/miniconda3 ~/anaconda3 ~/miniforge3 2>/dev/null

# Removes downloaded tarballs, unused packages, and caches (safe)
conda clean --all
```

#### 6.3.9 Ruby (rbenv / gems)

**Identify:**
```bash
du -sh ~/.rbenv ~/.gem 2>/dev/null
rbenv versions 2>/dev/null
```

**Clean:**
```bash
# Remove a specific old Ruby version (safe - active version remains)
# rbenv uninstall <version>

# Removes older versions of installed gems (safe)
gem cleanup
```

#### 6.3.10 Node.js runtime managers (nvm / Volta / fnm / Bun / Deno)

**nvm:**
```bash
# Identify old versions
nvm ls 2>/dev/null
du -sh ~/.nvm/versions 2>/dev/null

# Remove a specific old version (safe)
# nvm uninstall <version>
```

**Volta:**
```bash
du -sh ~/.volta 2>/dev/null
# Volta has no CLI command for removing specific runtime versions
# Remove a specific Node.js version manually (safe - active version remains)
# ls ~/.volta/images/node
# rm -rf ~/.volta/images/node/v<version>
```

**fnm:**
```bash
du -sh ~/.local/share/fnm "$HOME/Library/Application Support/fnm" 2>/dev/null
# Remove a specific old version (safe)
# fnm uninstall <version>
```

**Bun:**
```bash
# Identify
du -sh ~/.bun 2>/dev/null

# Removes Bun package cache (safe - re-downloaded on next install)
bun pm cache rm
```

**Deno:**
```bash
# Identify - the module cache lives at DENO_DIR (macOS default
# ~/Library/Caches/deno; confirm with `deno info`)
du -sh ~/Library/Caches/deno 2>/dev/null

# Removes Deno module cache (safe - re-downloaded on next import)
deno clean

# Note: ~/.deno holds executables from `deno install`, not the cache
```

#### 6.3.11 SDKMAN

**Identify:**
```bash
du -sh ~/.sdkman/candidates ~/.sdkman/archives 2>/dev/null
sdk list java 2>/dev/null
```

**Clean:**
```bash
# Removes downloaded archives and temp files (safe)
sdk flush

# Remove a specific old SDK version (safe - active version remains)
# sdk uninstall java <identifier>
```

#### 6.3.12 PHP (Composer)

**Identify:**
```bash
du -sh ~/.composer 2>/dev/null
```

**Clean:**
```bash
# Removes Composer package cache (safe - re-downloaded on next install)
composer clear-cache
```

#### 6.3.13 Elixir/Erlang (hex / mix)

**Identify:**
```bash
du -sh ~/.hex ~/.mix 2>/dev/null
```

**Clean:**
```bash
# Removes hex package registry cache (safe - re-downloaded on next mix deps.get)
rm -rf ~/.hex/packages/hexpm

# WARNING: Removes all compiled mix dependencies across environments
# mix deps.clean --all must be run per-project to rebuild
# rm -rf ~/.mix/archives
```

#### 6.3.14 Dart (pub)

**Identify:**
```bash
du -sh ~/.pub-cache 2>/dev/null
```

**Clean:**
```bash
# Removes pub package cache (safe - re-downloaded on next pub get)
dart pub cache clean

# If using Flutter:
# flutter pub cache clean
```

#### 6.3.15 Lua (LuaRocks)

**Identify:**
```bash
du -sh ~/.luarocks 2>/dev/null
```

**Clean:**
```bash
# Remove old versions of installed rocks (safe - current versions remain)
# --tree is required: purge does not assume a default tree
luarocks purge --old-versions --tree ~/.luarocks

# WARNING: Removes all user-installed Lua rocks
# rm -rf ~/.luarocks
```

#### 6.3.16 R

**Identify:**
```bash
du -sh ~/Library/R 2>/dev/null
```

**Clean:**
```bash
# Remove old packages via R console (safe - specify packages to remove)
# Rscript -e 'remove.packages(c("packagename"))'

# WARNING: Removes all user-installed R packages for a given R version
# rm -rf ~/Library/R/<version>/library
```

#### 6.3.17 Perl (cpanm)

**Identify:**
```bash
du -sh ~/perl5 ~/.cpanm 2>/dev/null
```

**Clean:**
```bash
# Removes cpanm build and work files (safe - not the installed modules)
rm -rf ~/.cpanm/work

# WARNING: Removes all user-installed Perl modules
# rm -rf ~/perl5
```

#### 6.3.18 Groovy (Grape)

**Identify:**
```bash
du -sh ~/.groovy/grapes 2>/dev/null
```

**Clean:**
```bash
# Removes Grape dependency cache (safe - re-downloaded on next @Grab use)
rm -rf ~/.groovy/grapes
```

#### 6.3.19 Nim (nimble)

**Identify:**
```bash
du -sh ~/.nimble 2>/dev/null
```

**Clean:**
```bash
# WARNING: Removes all installed Nimble packages - must reinstall manually
# nimble remove <packagename>
# rm -rf ~/.nimble/pkgs
```

#### 6.3.20 Zig

**Identify:**
```bash
du -sh ~/.zig 2>/dev/null
```

**Clean:**
```bash
# Removes project-level build cache (safe - run from project directory)
rm -rf .zig-cache

# Removes global Zig build cache
rm -rf ~/.cache/zig

# Remove old Zig toolchain versions manually (keep active version)
# ls ~/.zig
```

#### 6.3.21 V (vlang)

**Identify:**
```bash
du -sh ~/.vmodules 2>/dev/null
```

**Clean:**
```bash
# WARNING: Removes all installed V modules - must reinstall manually
# v remove <module>
# rm -rf ~/.vmodules
```

#### 6.3.22 Version managers (asdf / mise)

**asdf:**
```bash
# Identify installed versions
du -sh ~/.asdf 2>/dev/null
asdf list 2>/dev/null

# Remove a specific old version (safe - active version remains)
# asdf uninstall <plugin> <version>

# Remove an unused plugin entirely (safe)
# asdf plugin remove <plugin>
```

**mise:**
```bash
# Identify
du -sh ~/.local/share/mise 2>/dev/null
mise ls 2>/dev/null

# Removes all inactive/old tool versions (safe - active versions remain)
mise prune
```

---

### 6.4 IDE caches and extensions

#### 6.4.1 VS Code

**Identify:**
```bash
du -sh ~/.vscode/extensions 2>/dev/null
du -sh ~/Library/Application\ Support/Code/Cache 2>/dev/null
```

**Clean:**
```bash
# Removes cached files only (safe - extensions and settings remain)
rm -rf ~/Library/Application\ Support/Code/Cache/*

# To remove unused extensions, use VS Code UI or:
# code --list-extensions
# code --uninstall-extension <extension-id>
```

#### 6.4.2 JetBrains IDEs (IntelliJ, PyCharm, WebStorm, GoLand, etc.)

**Identify:**
```bash
du -sh ~/Library/Caches/JetBrains 2>/dev/null
du -sh ~/Library/Logs/JetBrains 2>/dev/null
```

**Clean:**
```bash
# Removes caches and logs (safe - will regenerate)
rm -rf ~/Library/Caches/JetBrains
rm -rf ~/Library/Logs/JetBrains
```

---

## 7. User application caches

**Identify:**
```bash
du -sh ~/Library/Caches/* 2>/dev/null | sort -h
```

Many high-usage entries (Google, Slack ShipIt, Homebrew, Spotify, go-build, etc.) are safe to clear.

**Clean:**
```bash
# Close affected apps first (browsers, Slack, Spotify, etc.)

# SAFEST: Delete specific caches only (examples)
rm -rf ~/Library/Caches/Google
rm -rf ~/Library/Caches/Homebrew
rm -rf ~/Library/Caches/com.tinyspeck.slackmacgap.ShipIt
rm -rf ~/Library/Caches/com.spotify.client

# WARNING: Deletes ALL user app caches - very aggressive
# Only use if you understand the impact and have closed all apps
# rm -rf ~/Library/Caches/*
```

Expect slower first launches after clearing caches.

---

## 8. System data and local backups

### 8.1 Old software updates

**Identify:**
```bash
# Per-user update/download cache (App Store and some updaters)
du -sh ~/Library/Updates 2>/dev/null
```

**Clean:**
```bash
# Removes old per-user update/download files
# Note: macOS or the App Store will re-download updates if needed
rm -rf ~/Library/Updates/*
```

### 8.2 System-level caches

**Identify:**
```bash
du -sh /Library/Caches 2>/dev/null
sudo du -sh /Library/Caches/* 2>/dev/null | sort -h
```

**Clean:**
```bash
# IMPORTANT: Close all applications first
# Review output first - do NOT use wildcard deletion
# Only delete caches for apps you recognise and have closed
# System-level caches can affect multiple apps

# Safe examples (close Safari/browsers first):
sudo rm -rf /Library/Caches/com.apple.Safari
sudo rm -rf /Library/Caches/org.mozilla.firefox

# For other caches, research the bundle ID before deleting
```

In general, system caches can be cleared safely if the corresponding apps are closed, but deleting the wrong thing under `/Library/Caches` may cause temporary issues. Prefer targeting caches for specific apps you recognise rather than broad wildcard deletion.

### 8.3 System logs

**Identify:**
```bash
sudo du -sh /private/var/log 2>/dev/null
sudo du -sh /private/var/log/* 2>/dev/null | sort -h
```

**Clean:**
```bash
# Removes old compressed log files only (safe - current logs remain)
sudo rm -f /private/var/log/*.gz
```

---

## 9. Old macOS system data (Previous System)

**Identify:**
```bash
sudo du -sh /System/Volumes/Data/Previous\ System* 2>/dev/null
```

**Clean:**
```bash
# ⚠️ CRITICAL WARNING ⚠️
# This removes your ability to roll back to the previous macOS version
# Only delete if:
#   1. Current macOS version is stable (30+ days since upgrade)
#   2. You have a complete Time Machine or other backup
#   3. You will not need to downgrade
# If unsure, DO NOT DELETE - macOS may remove this automatically after some time

sudo rm -rf /System/Volumes/Data/Previous\ System*
```


