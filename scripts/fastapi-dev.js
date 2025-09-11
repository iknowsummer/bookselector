const { spawn } = require("child_process");

// backendディレクトリでuvicornをリロード付きで起動
const proc = spawn("uv", ["run", "uvicorn", "main:app", "--reload"], {
  cwd: "backend/app",
  stdio: "inherit",
  shell: true,
});

proc.on("close", (code) => {
  process.exit(code);
});
