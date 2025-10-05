# Nix configuration for Replit
# Defines system packages needed for Signal RAG Bot

{ pkgs }: {
  deps = [
    # Python 3.11
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools

    # Java (required for signal-cli)
    pkgs.jdk17_headless

    # System utilities
    pkgs.wget
    pkgs.curl
    pkgs.git

    # Build tools (for compiling Python packages)
    pkgs.gcc
    pkgs.gnumake

    # SSL certificates
    pkgs.cacert

    # Process management
    pkgs.procps

    # For health checks
    pkgs.bash
  ];

  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
      pkgs.glib
      pkgs.xorg.libX11
    ];

    # Java home for signal-cli
    JAVA_HOME = "${pkgs.jdk17_headless}";

    # Python optimization
    PYTHONUNBUFFERED = "1";
    PYTHONOPTIMIZE = "1";
  };
}
