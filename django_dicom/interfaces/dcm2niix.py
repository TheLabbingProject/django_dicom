import os
import subprocess

DCM2NIIX = os.getenv("DCM2NIIX")
FLAGS = {"compressed": "-z", "BIDS": "-b", "name": "-f", "directory": "-o"}
BOOLEAN = {True: "y", False: "n"}


def generate_command(
    path: str,
    directory: str,
    name: str,
    compressed: bool = True,
    generate_json: bool = True,
) -> list:
    return [
        DCM2NIIX,
        FLAGS["compressed"],
        BOOLEAN[compressed],
        FLAGS["BIDS"],
        BOOLEAN[generate_json],
        FLAGS["directory"],
        directory,
        FLAGS["name"],
        name,
        path,
    ]


def convert(
    path: str,
    directory: str,
    name: str,
    compressed: bool = True,
    generate_json: bool = False,
):
    command = generate_command(
        path, directory, name, compressed=compressed, generate_json=generate_json
    )
    try:
        subprocess.check_output(command)
        output_path = os.path.join(directory, f"{name}.nii.gz")
        if os.path.isfile(output_path):
            return output_path
        else:
            raise RuntimeError(
                "Failed to create NIfTI file using dcm2niix! Please check application configuration"
            )
    except FileNotFoundError:
        raise NotImplementedError(
            "Could not call dcm2niix! Please check settings configuration."
        )

