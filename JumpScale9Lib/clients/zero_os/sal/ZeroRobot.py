import time


class ZeroRobot:
    """
    Zero robot
    """

    def __init__(self, container, port=6600, telegram_bot_token=None, telegram_chat_id=0, template_repos=None):
        self.id = 'zbot.{}'.format(container.name)
        self.container = container
        self.port = port
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.template_repos = template_repos if template_repos else list()

    def start(self, timeout=120):
        if self.is_running():
            return

        container_client = self.container.client
        container_fs = container_client.filesystem

        init_done_file = "/root/.jumpscale_init_done"
        if not container_fs.exists(init_done_file):
            # Check ssh-key
            ssh_key_path = "/root/.ssh/id_rsa"
            if not container_fs.exists(ssh_key_path):
                cmd_line = 'ssh-keygen -t rsa -N "" -f %s' % ssh_key_path
                result = container_client.system(cmd_line).get()
                if result.code != 0:
                    raise RuntimeError("Could not generate sshkey!\nstdout: %s\nstderr: %s" % (result.stdout, result.stderr))

            # Check repos
            repo_base_dir = '/opt/code/local/local/zbot_%s' 
            for repo in ("config", "data"):
                repo_dir = repo_base_dir % repo
                if not container_fs.exists("%s/.git" % repo_dir):
                    container_fs.mkdir(repo_dir)
                    result = container_client.system("git init .",  dir=repo_dir).get(timeout=timeout)
                    if result.code != 0:
                        raise RuntimeError("Could not init %s repo!\nstdout: %s\nstderr: %s", repo, result.stdout, result.stderr)
            
            # Init jumpscale
            cmd_line = "js9_config init -s -k %s -p %s" % (ssh_key_path, repo_base_dir % 'config')
            result = container_client.system(cmd_line).get(timeout=timeout)
            if result.code != 0:
                raise RuntimeError("Could not init jumpscale!\nstdout: %s\nstderr: %s" % (result.stdout, result.stderr))

            container_client.system("touch %s" % init_done_file)
        
        cmd_line = "zrobot server start --listen :%s --data-repo git@local/local/zbot_data --config-repo git@local/local/zbot_config" % self.port
        for templateRepo in self.template_repos:
            cmd_line += " --template-repo %s" % templateRepo
        if self.telegram_bot_token:
            cmd_line += " --telegram-bot-token %s" % self.telegram_bot_token
        if self.telegram_chat_id:
            cmd_line += " --telegram-chat-id %s" % self.telegram_chat_id
        cmd = container_client.system(cmd_line, id=self.id)
        start = time.time()
        while not self.container.is_port_listening(self.port, 2):
            if not self.is_running():
                result = cmd.get()
                raise RuntimeError("Could not start 0-robot.\nstdout: %s\nstderr: %s" % (result.stdout, result.stderr))
            if time.time() > start + timeout:
                container_client.job.kill(self.id, signal=9)
                result = cmd.get()
                raise RuntimeError("Zero robot failed to start within %s seconds!\nstdout: %s\nstderr: %s", (timeout, result.stdout, result.stdout))
    
    def is_running(self):
        return self.container.is_job_running(self.id)

    def stop(self, timeout=60):
        if not self.is_running():
            return

        self.container.client.job.kill(self.id)
        for _ in range(timeout):
            if not self.is_running():
                return
            time.sleep(1)
        self.container.client.job.kill(self.id, signal=9)
