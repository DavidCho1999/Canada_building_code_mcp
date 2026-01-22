# 개발 서버 시작

Next.js 개발 서버를 안전하게 시작합니다.

## 실행 순서

1. **포트 3001 사용 중인 프로세스 확인**
   ```bash
   netstat -ano | findstr :3001
   ```

2. **사용 중이면 프로세스 종료** (PID 확인 후)
   ```bash
   taskkill /PID <PID> /F
   ```

3. **.next/dev/lock 파일 삭제** (존재하면)
   ```bash
   rm -f codevault/.next/dev/lock
   ```

4. **서버를 백그라운드에서 시작**
   ```bash
   cd codevault && npm run dev
   ```
   - `run_in_background: true` 옵션 사용
   - 서버 시작 후 3초 대기

5. **서버 상태 확인**
   - http://localhost:3001 접속 가능한지 확인

## 주의사항

- 서버 명령은 반드시 **백그라운드**에서 실행 (튕김 방지)
- lock 파일 충돌 시 Claude Code가 종료될 수 있음
- 포트 충돌 확인 필수