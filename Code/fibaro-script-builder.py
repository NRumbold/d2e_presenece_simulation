import sys, getopt, os, re, shutil, json

import pysftp as pysftp


def getScriptArguments(argv):
    source_path = ''
    config_path = ''
    deploy_config_path = ''
    force = False

    try:
        opts, args = getopt.getopt(argv, "hs:c:df",
                                   ["help", "sourcepath=", "configpath=", "deployconfigpath=", "force"])
    except getopt.GetoptError:
        print("fibaro-script-builder.py -s <sourcepath> -c <configpath> -d [deploconfigpath]")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print("fibaro-script-builder.py -s <sourcepath> -c <configpath> -d [deploconfigpath]")
            sys.exit()
        elif opt in ("-s", "--sourcepath"):
            source_path = arg
        elif opt in ("-c", "--configpath"):
            config_path = arg
        elif opt in ("-d", "--deployconfigpath"):
            deploy_config_path = arg
        elif opt in ("-f", "--force"):
            force = True

    if source_path == "":
        raise getopt.GetoptError("Source path missing!")

    if config_path == "":
        raise getopt.GetoptError("Config path missing!")

    return {
        "source_path": source_path,
        "config_path": config_path,
        "deploy_config_path": deploy_config_path,
        "force": force
    }


def is_dir_exists(path):
    return os.path.exists(path)


def create_dir(dir_name, force):
    if os.path.exists(dir_name):
        if not force:
            user_choice = input(
                f"Are you sure you want to overwrite the contents of the directory: {dir_name}\n(Y/n)").lower()
            if not user_choice == "" or not user_choice == "y":
                sys.exit(0)

        clear_directory(dir_name)

    os.mkdir(dir_name)
    print(f"Directory {dir_name} created")


def clear_directory(dir_name):
    if os.path.exists(dir_name):
        # os.rmdir(dir_name)
        shutil.rmtree(dir_name)
        print(f"Directory {dir_name} removed")


def print_dir_and_files(source_path):
    print("")
    for root, dirs, files in os.walk(source_path):
        print(f"----- List of files ({len(files)}) in {root} -----")
        for file in files:
            print(f"\t - {file}")
        print("------------------------------------------\n")


def replace_src_with_dest_path(path, source_path, destination_path):
    return path.replace(source_path, destination_path, 1)


def create_file(file_path):
    return open(file_path, "w+")


def remove_file(file_path):
    open(file_path, 'w').close()


def is_import_statement(line):
    match = re.search(r"--#import\(\".+\"\)", line)
    return match is not None


def is_config_statement(line):
    match = re.search(r"--#config\(\".+\"\)", line)
    return match is not None


def get_import_statement(line):
    match = re.search(r"\"(.+)\"", line)
    return match.group(1)


def get_file_content(file_path):
    file = open(file_path, "r")
    file_content = file.read()
    file.close()
    return file_content


def get_json_keys(json_string):
    # 	GlobalVariables.debugVarName
    json_keys = json_string.split(".")
    return json_keys


def create_remote_dir_if_not_exists(sftp, dir_name):
    if sftp.exists(dir_name):
        print(f"Directory '{dir_name}' already exists")
    else:
        print(f"Creating directory '{dir_name}'")
        sftp.mkdir(dir_name)


arguments = getScriptArguments(sys.argv[1:])
source_path = arguments["source_path"]
destination_path = "dist"
config_path = arguments["config_path"]
deploy_config_path = arguments["deploy_config_path"]
force = arguments["force"]

if not is_dir_exists(source_path):
    raise IOError(f"Cannot find source directory: {source_path}")

if not is_dir_exists(config_path):
    raise IOError(f"Cannot find config file: {config_path}")

create_dir(destination_path, force)

print_dir_and_files(source_path)

is_root_folder = True
create_dir("tmp", force)
config_json = json.loads(get_file_content(config_path))

for root, dirs, files in os.walk(source_path):
    new_path = replace_src_with_dest_path(root, source_path, destination_path)

    if not is_root_folder:
        create_dir(new_path, force)

    for file_name in files:
        src_file_path = os.path.join(root, file_name)
        dest_file_path = os.path.join(new_path, file_name)
        tmp_file_path = os.path.join("tmp", file_name)
        create_file(tmp_file_path)
        src_file = open(src_file_path, "r")
        tmp_file = open(tmp_file_path, "a")

        for line in src_file:
            if is_import_statement(line):
                import_path = get_import_statement(line)
                if not is_dir_exists(import_path):
                    raise IOError(f"Couldn't import file from {import_path}. It does not exist")
                else:
                    import_file_content = get_file_content(import_path)
                    tmp_file.write(import_file_content)
            elif is_config_statement(line):
                config_path = get_import_statement(line)
                config_keys = get_json_keys(config_path)
                config_value = config_json["config"]
                for config_key in config_keys:
                    config_value = config_value[config_key]

                tmp_file.write(f"{config_value}\n")

            else:
                tmp_file.write(line)

        src_file.close()
        tmp_file.close()
        shutil.copyfile(tmp_file_path, dest_file_path)
        remove_file(tmp_file_path)

    is_root_folder = False

clear_directory("tmp")

# OBFUSCATE


# DEPLOY
if deploy_config_path != "":
    print("\n==============DEPLOY==============")
    hc = json.loads(get_file_content(deploy_config_path))
    os.chdir('dist')
    print(f"Deploying files to {hc['hcSerialNumber']} ({hc['description']})")

    with pysftp.Connection('hourwork.tech', username='root', private_key='~/.ssh/id_rsa') as sftp:
        with sftp.cd('/var/www/html/fibaroDeploy'):
            create_remote_dir_if_not_exists(sftp, hc['hcSerialNumber'])
            with sftp.cd(hc['hcSerialNumber']):
                if is_dir_exists("QuickApps"):
                    print("Some QuickApps exists...")
                    create_remote_dir_if_not_exists(sftp, "QuickApps")
                    with sftp.cd("QuickApps"):
                        os.chdir('QuickApps')
                        print(f"Copying QuickApps")
                        for dir in hc['quickApps']:
                            print(f"Copying files from {dir} to {hc['quickApps'][dir]['id']}")
                            QA_ID = str(hc['quickApps'][dir]['id'])
                            if not sftp.exists(QA_ID):
                                print(f"Creating directory '{QA_ID}'")
                                sftp.mkdir(QA_ID)

                            sftp.put_r(dir, QA_ID)
                            print("Copying QuickApps files completed\n")

                        os.chdir("..")

                if is_dir_exists("Scenes"):
                    print("Some Scenes exists...")
                    create_remote_dir_if_not_exists(sftp, "Scenes")
                    with sftp.cd("Scenes"):
                        os.chdir("Scenes")
                        print(f"Copying Scenes")
                        for dir in hc['scenes']:
                            print(f"Copying files from {dir} to {hc['scenes'][dir]['id']}")
                            Scene_ID = str(hc['scenes'][dir]['id'])
                            if not sftp.exists(Scene_ID):
                                print(f"Creating directory '{Scene_ID}'")
                                sftp.mkdir(Scene_ID)

                            sftp.put_r(dir, Scene_ID)
                            print("Copying scenes files completed\n")

                        os.chdir("..")

                # Generate config file
                print("Generating config file...")
                config_file = create_file("./config.json")
                print("config.json created")
                config = {}

                if is_dir_exists("QuickApps"):
                    print("\nAdding QuickApps to config...")
                    os.chdir('QuickApps')
                    quick_apps = []
                    for dir, quick_app in hc['quickApps'].items():
                        dist_qa = {
                            "id": quick_app['id'],
                            "disabled": quick_app['disabled']
                        }
                        os.chdir(dir)
                        for root, dirs, files in os.walk('.'):
                            dist_qa['files'] = files

                        print(f"QuickApp '{dir}' config: {json.dumps(quick_app)}")
                        quick_apps.append(dist_qa)
                        os.chdir('..')
                    config['QuickApps'] = quick_apps
                    print("Adding QuickApps to config completed")
                    os.chdir('..')


                if is_dir_exists("Scenes"):
                    print("\nAdding Scenes to config...")
                    os.chdir('Scenes')
                    scenes = []
                    for dir, scene in hc['scenes'].items():
                        dist_scene = {
                            "id": scene['id'],
                            "disabled": scene['disabled']
                        }
                        print(f"Scene '{dir}' config: {json.dumps(scene)}")
                        scenes.append((dist_scene))
                    os.chdir('..')
                config['Scenes'] = scenes
                print("Adding Scenes to config completed")
                os.chdir('..')

                config_file.write(json.dumps(config))
                config_file.close()

                print("\nDeploying config file...")
                os.chdir('dist')
                sftp.put('config.json')
                print("Config file deployed")