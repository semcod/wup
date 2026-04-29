# WUP Development TODO

## High Priority

### Testing & Validation
- [ ] Test `wup assistant` on c2004 project (/home/tom/github/maskservice/c2004)
- [ ] Verify anomaly detection on c2004 YAML configs
- [ ] Test browser notifications with wupbro on c2004
- [ ] Validate all detection methods (hash, structure, ast)

### Bug Fixes
- [ ] Fix any import issues in assistant.py when running on real project
- [ ] Ensure ServiceType import works correctly in all contexts
- [ ] Verify notification SSE connection stability under load

## Medium Priority

### Enhancements
- [ ] Add progress bar to assistant for long operations
- [ ] Implement dry-run mode for assistant (`wup assistant --dry-run`)
- [ ] Add export to different formats (JSON, TOML) for assistant
- [ ] Create web-based configuration UI (alternative to CLI assistant)
- [ ] Add support for more frameworks (NestJS, Spring Boot, Laravel)

### Documentation
- [ ] Add troubleshooting guide for common setup issues
- [ ] Create video tutorial for first-time users
- [ ] Add architecture diagrams to docs/
- [ ] Document performance benchmarks

### Anomaly Detection
- [ ] Add machine learning-based anomaly detection option
- [ ] Implement severity prediction based on change patterns
- [ ] Add historical trend analysis
- [ ] Create anomaly detection presets for common file types

## Low Priority

### Nice to Have
- [ ] VS Code extension for WUP
- [ ] GitHub Action for WUP
- [ ] Docker image with WUP pre-installed
- [ ] Helm chart for Kubernetes deployment
- [ ] Mobile app for notifications (companion to wupbro)

## Testing Checklist for c2004

### Assistant Testing
- [ ] Run `wup assistant --quick` on c2004
- [ ] Verify FastAPI auto-detection works
- [ ] Check service auto-detection for connect-* modules
- [ ] Validate generated wup.yaml structure
- [ ] Test interactive mode with all menus

### Anomaly Detection Testing
- [ ] Run hash detection on c2004 configs
- [ ] Test YAML structure detection
- [ ] Verify AST detection on Python files
- [ ] Check performance (< 100ms for typical file)
- [ ] Validate reporting format

### Notification Testing
- [ ] Start wupbro server
- [ ] Enable notifications in dashboard
- [ ] Send test notification
- [ ] Trigger real event and verify notification
- [ ] Test SSE reconnection
- [ ] Verify cooldown works

## Completed

- [x] Rename wup-web to wupbro
- [x] Create notification system with 7 types
- [x] Implement SSE for real-time notifications
- [x] Create configuration assistant
- [x] Add fast anomaly detection methods
- [x] Create comprehensive documentation
- [x] Update CLI with assistant command
- [x] Add anomaly detection config to models
