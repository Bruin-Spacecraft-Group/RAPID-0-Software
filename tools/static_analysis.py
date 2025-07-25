import os
import deploy_to_usb
import subprocess

config_path = os.path.abspath(os.path.join("config", "pylama.cfg"))
analysis_passed = True

for app in os.listdir("artifacts"):
    if (len(app) < 8) or (app[-8:] != "_testapp"):
        deploy_path = deploy_to_usb.deploy_with_settings(app, None, True, False)
        pylama = subprocess.run(
            ["pylama", "-o", config_path, deploy_path],
            cwd=deploy_path,
        )
        if pylama.returncode != 0:
            analysis_passed = False

exit(0 if analysis_passed else 1)
