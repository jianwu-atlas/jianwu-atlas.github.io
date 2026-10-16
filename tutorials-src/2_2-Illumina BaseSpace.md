---
title: "Illumina BaseSpace: scRNA-seq Analysis with the DRAGEN Pipeline"
date: 2026-07-29
summary: "介绍如何在 Illumina BaseSpace 平台上使用 DRAGEN Single Cell RNA 流程分析 scRNA-seq 数据，涵盖账号注册、CLI 安装配置，以及项目文件的上传下载操作。"
type: tutorial
tags: ["Jian Wu", "jwtools", "Illumina", "BaseSpace", "DRAGEN", "scRNA-seq", "CLI"]
cover: "https://jianwu-atlas.github.io/assets/img/logos/jianwu_social_preview.png"
#cover: "https://jianwu-atlas.github.io/assets/img/logos/jwtools_logo_social_preview.png"
#cover: "https://github.com/jianwu-atlas/jwtools/raw/main/man/figures/logo.png"
---

👤 Analysis by: Vishnu Kumar and Marek Bartkuhn

## scRNA-seq Analysis Using Illumina DRAGEN Pipeline

1. Make an account on Illumina BaseSpace:
   <https://login.illumina.com/platform-services-manager/?rURL=https://basespace.illumina.com&clientId=basespace&clientVars=aHR0cDovL2Jhc2VzcGFjZS5pbGx1bWluYS5jb20vZGFzaGJvYXJk&redirectMethod=GET#/register>
2. Here, we can create different projects. Within a specific project, we can upload files either by drag-and-drop or using the **CLI**.
3. To run a specific app, go to the **Apps** tab and type "single cell". This will display the **DRAGEN Single Cell RNA** app. Click on it to open this app, where you can view pipeline information, input file requirements, and other relevant details. Then click **Launch Application**, select the required input files and parameters, and run the analysis.

## Install BaseSpace Sequence Hub CLI

Documentation: <https://developer.basespace.illumina.com/docs/content/documentation/cli/cli-overview>

Installation for Linux is given below.

### Installation for Linux

```bash
# make directory
$ mkdir -p $HOME/bin
$ wget "https://launch.basespace.illumina.com/CLI/latest/amd64-linux/bs" -O $HOME/bin/bs

# file permissions
$ chmod u+x $HOME/bin/bs
```

### Authenticate to EU server

```bash
$ bs auth --api-server https://api.euc1.sh.basespace.illumina.com
```

You will get a URL — paste it into a browser to complete authentication.

### Inspect the token

```bash
$ bs whoami
```

### Configure the server to EU

```bash
$ eval $(bs load config eu)

# list projects
$ bs list projects

# list app sessions
$ bs list appsession
```

## Command-Line Reference

<https://developer.basespace.illumina.com/docs/content/documentation/cli/cli-examples#FASTQupload>

### Upload and download files

```bash
# upload folder /files
$ bs upload dataset -p <ProjectID> --recursive .

# download a complete project
$ bs download project -i <ProjectID> -o <output>

# download specific data
$ bs download appsession --id <APPSESSION_ID> --output <LOCAL_FOLDER>
```
