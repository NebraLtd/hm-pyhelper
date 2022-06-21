"""
This script creates:
1. Github repositories for backing openfleets.
2. Openfleets and commercial fleets based on a consistent format.

Preconditions:
Before executing this script, githbub cli "gh" and balena cli "balena"
should be installed and logged in.

Some things will have to be done manually due to lack of support from gh
or balena cli.
Manual steps required after running this script:
1. Link the fleet to its github repo.
2. Make the fleet public which effectively makes it openfleet. This step can't be
done before step 1.
3. Link the fleet url in github description. gh cli provides a homepage option while
creating repos but not while you are creating it from a template.
"""

import traceback
import subprocess
import hm_pyhelper.hardware_definitions as hdf


# openfleet will only have mainnet fleets.
FLEET_TYPE_NETWORK_MAP = {'commercial': ['mainnet', 'testnet'], 'openfleet': ['mainnet']}
COMMERCIAL_FLEET_ENVIRONMENT = {
    'SENTRY_CONFIG': 'https://3234e2c67fe04c3e9f8b0c9b118c415a@o571444.ingest.sentry.io/5725518',
    'SENTRY_DIAG': 'https://1f07be71da9c45039d6946f498335d30@o571444.ingest.sentry.io/5730184',
    'SENTRY_PKTFWD': 'https://ebf665e3c1a647e496a6d823fcf36148@o571444.ingest.sentry.io/5730185',
    'HELIUM_MINER_HEIGHT_URL':
        'https://fuzzy-marmalade-warlock.skittles.stakejoy.com/v1/blocks/height',
}
OPENFLEET_ENVIRONMENT = {
    'HELIUM_MINER_HEIGHT_URL': 'https://api.helium.io/v1/blocks/height',
}

# production configuration
GITHUB_ORG = "NebraLtd"
OPENFLEET_TEMPLATE_REPO = "NebraLtd/hnt_openfleet_template"


def filter_lower(list: list):
    return [x for x in list if x.islower()]


def get_fleets():
    return list(fleets.keys())


def get_repositories():
    return list(set(fleets.values()))


# create public github repo
def create_repo(repo_name, variant):
    try:
        print(f"creating repo {repo_name}")
        # Note: -t and -h options are not supported with templates
        repo_create_command = [
            "gh", "repo", "create", f"{GITHUB_ORG}/{repo_name}",
            "-p", OPENFLEET_TEMPLATE_REPO, "--public",
            "-d", f"Balena OpenFleet for {hdf.variant_definitions[variant]['FRIENDLY']} Miners"
        ]
        subprocess.run(repo_create_command)
    except Exception as e:
        print(f"failed to create repo {repo_name} : {e}")
        traceback.print_exc()


def create_fleet(fleet_name, variant):
    try:
        # fleets have to made public manually later
        print(f"creating fleet: {fleet_name}")
        fleet_create_command = [
            "balena", "fleet", "create", "--type",
            str(hdf.variant_definitions[variant]["BALENA_DEVICE_TYPE"][0]),
            fleet_name
        ]
        subprocess.run(fleet_create_command)
    except Exception as e:
        print(f"failed to create fleet {fleet_name} : {e}")
        traceback.print_exc()


def update_fleet_environment(fleet_name, fleet_type, variant):
    base_env = COMMERCIAL_FLEET_ENVIRONMENT
    if fleet_type == 'openfleet':
        base_env = COMMERCIAL_FLEET_ENVIRONMENT
    fleet_env = base_env.copy()
    fleet_env['VARIANT'] = variant

    for key, value in fleet_env.items():
        print(f"updating fleet {fleet_name} environment variable {key} to {value}")
        try:
            subprocess.run(["balena", "env", "add", "--fleet", fleet_name, key, value])
        except Exception as e:
            print(f"failed to add {fleet_name}'s environment variable {key} : {value} with {e}")


fleets = {}  # map of desired fleet name to github repo name
for variant in filter_lower(list(hdf.variant_definitions.keys())):
    if variant.islower():
        # openfleet repos are per variant.
        repo = f"hnt_{variant}"
        create_repo(repo, variant)
        for fleet_type in FLEET_TYPE_NETWORK_MAP:
            for network in FLEET_TYPE_NETWORK_MAP[fleet_type]:
                fleet = f"hnt_{variant}_{network}_{fleet_type}"
                fleets[fleet] = repo
                create_fleet(fleet, variant)
                update_fleet_environment(fleet, fleet_type, variant)


print("fleet names are:")
for fleet in get_fleets():
    print(fleet)

print("repo names are:")
for repo in get_repositories():
    print(repo)
