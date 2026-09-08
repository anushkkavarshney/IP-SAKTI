import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable automatic AGENTS.md/CLAUDE.md generation
  agentRules: false,
};

export default nextConfig;
