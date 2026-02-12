# TeamSBC Definitions

This repository contains the [image-builder](https://osbuild.org/docs/developer-guide/projects/image-builder/) definitions for the various TeamSBC artifacts. Artifacts are also built here through the use of GitHub actions.

## Downloads

Direct links to the latest builds of TeamSBC artifacts. Grouped by the Fedora version they are based on, and architecture.

### TeamSBC 44

#### x86_64

- [standard-virt](https://artifacts.teamsbc.net/main/latest/44/x86_64/teamsbc-44-standard-virt-x86_64.raw.xz)

#### aarch64

- [standard-virt](https://artifacts.teamsbc.net/main/latest/44/aarch64/teamsbc-44-standard-virt-aarch64.raw.xz)
- [standard-rpi3](https://artifacts.teamsbc.net/main/latest/44/aarch64/teamsbc-44-standard-rpi3-aarch64.raw.xz)
- [standard-rpi4](https://artifacts.teamsbc.net/main/latest/44/aarch64/teamsbc-44-standard-rpi4-aarch64.raw.xz)

### TeamSBC 45

#### x86_64

- [standard-virt](https://artifacts.teamsbc.net/main/latest/45/x86_64/teamsbc-45-standard-virt-x86_64.raw.xz)

#### aarch64

- [standard-virt](https://artifacts.teamsbc.net/main/latest/45/aarch64/teamsbc-45-standard-virt-aarch64.raw.xz)
- [standard-rpi3](https://artifacts.teamsbc.net/main/latest/45/aarch64/teamsbc-45-standard-rpi3-aarch64.raw.xz)
- [standard-rpi4](https://artifacts.teamsbc.net/main/latest/45/aarch64/teamsbc-45-standard-rpi4-aarch64.raw.xz)

## Building

You can build artifacts locally using the provided `Makefile` in this repository after you've installed the preqrequisites.

### Prerequisites

- `image-builder`

### Build

```
make build DISTRO=44 TYPE=standard-virt
```

Will build a TeamSBC Remix, Fedora 44 based `standard-virt` artifact.
