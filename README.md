# Vote

NTNU CSIE Database Theories final project.

## 架構

- 每個 domain 通常由 model, service, repository 組成，e.g. `User`, `UserService`, `UserRepository`
- FastAPI 這邊（那些 `vote.api` 底下的 code）會依賴 domain logic（`vote.domain`），web API 們通常就是 domain logic 的 thin wrapper
- 在 [`vote/api/__init__.py`](vote/api/__init__.py) 使用 FastAPI 的 `Dependes` 來注入 service 給 FastAPI 的 handler 使用
- domain 層的參數通常只有一個 `input`，會是個 pydantic 的 `BaseModel`，命名通常是 `XXXInput`，然後 FastAPI handler 這層的 IO 會是 `XXXRequest` / `XXXResponse`
- DB 使用 SurrealDB，可以使用 `start-db.sh` 來啟動 DB 的 container，但須注意目前沒有持久化，重開就沒了
