const { spawn } = require("child_process");

// backendディレクトリでuvicornをリロード付きで起動
// app.main:app 形式で、appパッケージのmainモジュールを指定
const proc = spawn("uv", [
  "run",
  "uvicorn",
  "app.main:app",
  "--reload",
  "--host", "0.0.0.0",
  "--port", "8000"
], {
  cwd: "backend",
  stdio: "inherit",
  shell: true,
});

proc.on("close", (code) => {
  process.exit(code);
});
