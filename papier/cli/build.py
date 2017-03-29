import os
import subprocess

from gallium import ICommand

GH_MARKUP_INST_CLI = ['gem', 'install', '-q', 'github-markup', 'github-markdown', 'redcarpet']


class DepsInstallationFailure(RuntimeError):
    """ Dependency Installation Failure """


class Build(ICommand):
    """ Build site """
    def identifier(self):
        return 'build'

    def define(self, parser):
        parser.add_argument(
            '--config',
            '-c',
            help     = 'the directory that contains the site configuration file',
            required = False,
            default  = os.path.join(os.getcwd(), 'papier.yml')
        )

        parser.add_argument(
            '--install-deps',
            '-i',
            help     = 'automatically install dependencies',
            required = False,
            action   = 'store_true'
        )

        parser.add_argument(
            '--watch',
            '-w',
            help     = 'enable live update',
            required = False,
            action   = 'store_true'
        )

    def execute(self, args):
        observer = None

        if args.install_deps and not self._install_dependencies():
            return

        if args.watch:
            observer = self.core.get('papier.live_updater')

        doc_tree = self.core.get('papier.assembler').assemble_by_file(args.config)

        if observer:
            observer.watch(args.src)
            observer.run_blocking_observation()

        print('[build] Complete without exciting incident')

    def _install_dependencies(self):
        try:
            subprocess.check_call('touch quick-test.md', shell = True)
            subprocess.check_call('github-markup quick-test.md > /dev/null', shell = True)
            subprocess.check_call('rm quick-test.md', shell = True)
        except FileNotFoundError:
            print('"github-markup" is not found.')

            to_install = self.ask(
                'Do you want to install it now?',
                choices = ('yes', 'no'),
                default = ''
            )

            if to_install == 'no':
                print('[build] Unable to continue until you install "github-markup"')

                return False

            try:
                self._install_github_markup()
            except DepsInstallationFailure as e:
                print('[build] {}: {}'.format(type(e).__name__, e))
                print('[build] Unable to continue without "github-markup"')

                return False

        return True

    def _install_github_markup(self):
        install_ok    = False
        install_err   = None
        attempt_count = 0
        attempts      = (
            ['sudo', '-H', *GH_MARKUP_INST_CLI],
            GH_MARKUP_INST_CLI,
        )

        for attempt in attempts:
            try:
                print('Executing: {}'.format(' '.join(attempt)))

                install_ok = subprocess.call(attempt) == 0
            except FileNotFoundError as e:
                insinstall_err = e

            if install_ok:
                install_err = None

                break

            attempt_count += 1

        if install_err:
            raise DepsInstallationFailure(str(install_err))

        if not install_ok:
            raise DepsInstallationFailure('Failed to install "github-markup"')
