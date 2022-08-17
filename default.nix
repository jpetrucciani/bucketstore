{ jacobi ? import
    (
      fetchTarball {
        name = "jpetrucciani-2022-08-17";
        url = "https://github.com/jpetrucciani/nix/archive/9e8f5c0b0f7f69257f7ff1c2032cbadbc3da7d25.tar.gz";
        sha256 = "1vyjwlhbqxfmm4xpvwyzvdl8k5jd5wg83avxlwpjkfh8yndm0bny";
      }
    )
    { }
}:
let
  inherit (jacobi.hax) ifIsLinux ifIsDarwin;

  name = "bucketstore";
  tools = with jacobi; {
    cli = [
      jq
      nixpkgs-fmt
    ];
    python = [
      (python310.withPackages (p: with p; [
        boto3

        # dev
        moto
        pytest
        pytest-cov
        tox
      ]))
    ];
  };

  env = jacobi.enviro {
    inherit name tools;
  };
in
env
