# jcode-fastapi

FastAPI dependency injection edges for [jcode](https://github.com/codewithjoe-tech/jcode).

## What it does

Detects FastAPI dependency injection patterns and emits typed `depends` edges in the jcode graph — so when you run `jcode_blast_radius` on a shared dependency, you instantly see every route that uses it.

| Pattern | Edge emitted |
|---------|-------------|
| `Depends(get_current_user)` | `depends`: route handler → `get_current_user` |
| `Security(verify_token)` | `depends`: route handler → `verify_token` |
| `Annotated[..., Depends(fn)]` | `depends`: route handler → `fn` |

## Install

```bash
jcode add fastapi
```

## How it works

Once installed, jcode auto-detects this plugin on any repo that has `fastapi` in its `requirements.txt` or `pyproject.toml`. No configuration needed.

```python
# jcode sees this:
@router.get("/users/me")
async def get_me(user: User = Depends(get_current_user)):
    ...

# and emits:
# get_me --[depends]--> get_current_user
```

So if you change `get_current_user`, `jcode_blast_radius` shows every route that will be affected.

## Part of the jcode ecosystem

- [jcode](https://github.com/codewithjoe-tech/jcode) — core CLI and MCP server
- [jcode-registry](https://github.com/codewithjoe-tech/jcode-registry) — plugin registry

---

Made by [Joel Thomas](https://codewithjoe.in)
