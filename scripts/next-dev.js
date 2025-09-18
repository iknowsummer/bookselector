const { spawn } = require("child_process");

const proc = spawn("npm", ["run", "dev"], {
  cwd: "frontend",
  stdio: "inherit",
  shell: true,
});

proc.on("close", (code) => {
  process.exit(code);
});
