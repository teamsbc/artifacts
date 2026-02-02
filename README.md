# TeamSBC Definitions

This repository contains the [image-builder](https://osbuild.org/docs/developer-guide/projects/image-builder/) definitions for the various TeamSBC artifacts. Artifacts are also built here through the use of GitHub actions.

## Building

You can build artifacts locally using the provided `Makefile` in this repository after you've installed the preqrequisites.

### Prerequisites

- `image-builder`

### Build

```
make build DISTRO=44 TYPE=standard-virt
```

Will build a TeamSBC Remix, Fedora 44 based `standard-virt` artifact.
