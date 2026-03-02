# Buenatura Agent-Zero Mobile Roadmap
**Status**: Approved for Development (March 2026)  
**Owner**: Valentin Kranz + C-Suite Agents  
**Priority**: High (Sovereign Local-First Product)

## Vision
Single cross-platform app (Android/iOS/Desktop/Web) running full agent-zero locally:
- Offline LLM inference (bundled models)
- Local repo storage (code/MD/Foam)
- Bidirectional sync (cloud/laptop/mobile)
- Browser access to local instance
- 85-90% feature parity with cloud/laptop

## Phase 1: MVP (2 Weeks, March 2026)
### Tech Stack
- **Framework**: Flutter/Dart (unified UI/logic)
- **LLM**: Rust FFI + llama.cpp (Phi-3-mini q4 bundled)
- **Repo**: git_dart + SQLite index
- **Memory**: LanceDB (local FAISS)
- **Sync**: Supabase deltas + GitHub push

### Deliverables
- APK prototype: Local chat + repo clone/edit
- 5-15 t/s inference on mid-Android
- Local HTTP server (browser: localhost:8080)
- GitHub fork integration

### Success Metrics
- APK <500MB
- Offline agent loop working
- Sync laptop ↔ mobile

## Phase 2: Full Parity (4 Weeks, April 2026)
- Python tool bridge (subprocess)
- Full Foam/MD editing + search
- Multi-model support (download)
- Cloud fallback for heavy tasks
- iOS/Desktop builds

## Phase 3: Polish (2 Weeks, May 2026)
- Battery optimization
- PWA web version
- App Store submission
- User testing (3 clients)

## Constraints
- No storage caps
- Sovereignty: Local-first, user owns repo/data
- YAGNI: Ship MVP fast

## Resources
- Flutter tutorial
- Rust FFI llama.cpp
- Phi-3-mini-q4.gguf model