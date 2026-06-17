COL1 = "\033[38;5;214m"  # orange
COL2 = "\033[38;5;220m"  # yellow
COL3 = "\033[38;5;230m"  # near white
RESET = "\033[0m"


def get_banner(version):

    print(f"{COL1}╔══════════════════════════════════════╗{RESET}")
    print(f"{COL1}║   Sunraise Agent Client (CLI) v0.1.0 ║{RESET}")
    print(f"{COL2}║   Enter '/q' or 'exit' to quit       ║{RESET}")
    print(f"{COL3}╚══════════════════════════════════════╝{RESET}\n")
