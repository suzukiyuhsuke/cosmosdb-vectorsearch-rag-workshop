FROM mcr.microsoft.com/devcontainers/python:3.10

# Node.jsのインストール
ARG NODE_VERSION="20"
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - && \
    apt-get update && \
    apt-get install -y nodejs && \
    npm install -g npm@latest

# 開発ツールのインストール
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    vim \
    jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python開発ツールのインストール
RUN pip install --upgrade pip && \
    pip install black pylint pipenv pre-commit

# ユーザー設定
ARG USERNAME=vscode
USER $USERNAME

# ワークスペースディレクトリ
WORKDIR /workspace
