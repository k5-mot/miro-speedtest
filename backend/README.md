# HELLO

## Windowsのdevcontainer前提条件

- SSHエージェントをWindows側で立てる
  - devcontainer側で、GitのSSH接続が可能になる。

```powershell
# 管理者権限で以下を実行
Set-Service -StartupType Automatic ssh-agent
Start-Service ssh-agent
```

```powershell
# ユーザ権限で以下を実行
ssh-add C:\Users\<username>\.ssh\id_rsa
```

```
uv run -- uvicorn main:app --reload
curl -X POST -F "file=@doc/sample.pdf" http://localhost:8000

uv run -- pre-commit install
```
