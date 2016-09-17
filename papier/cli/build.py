import logging
import subprocess

from gallium           import ICommand
from imagination.debug import get_logger

GH_MARKUP_INST_CLI = ['gem', 'install', '-q', 'github-markup', 'github-markdown', 'redcarpet']


class DepsInstallationFailure(RuntimeError):
    """ Dependency Installation Failure """


class Build(ICommand):
    """ Build site """
    def identifier(self):
        return 'build'

    def define(self, parser):
        parser.add_argument(
            '--src',
            '-s',
            help     = 'the directory containing the source of your website',
            required = True
        )

        parser.add_argument(
            '--output',
            '-o',
            help     = 'the directory will contain the actual website',
            required = True
        )

        parser.add_argument(
            '--base-path',
            '-b',
            help     = 'the URL base path',
            required = False,
            default  = ''
        )

        parser.add_argument(
            '--watch',
            '-w',
            help     = 'enable live update',
            required = False,
            action   = 'store_true'
        )

    def execute(self, args):
        logger   = self._logger()
        observer = None

        if not self._install_dependencies():
            return

        if args.watch:
            observer = self.core.get('papier.live_updater')

        nodes = self.core.get('papier.fs.walker').walk(args.src, args.output)

        self.core.get('papier.interpreter').prepare(nodes)
        self.core.get('papier.interpreter').process(nodes)

        print('\n'.join([
            '- {} ({})'.format(
                n.reference_path,
                'handled' if n.handler else 'not handled'
            )
            for n in nodes
        ]))

        if observer:
            observer.watch(args.src)
            observer.run_blocking_observation()

        logger.info('Complete without exciting incident')

    def _logger(self):
        return get_logger('builder', level = logging.DEBUG)

    def _install_dependencies(self):
        logger = self._logger()

        try:
            subprocess.check_call('github-markup > /dev/null', shell = True)
        except FileNotFoundError:
            print('"github-markup" is not found.')

            to_install = self.ask(
                'Do you want to install it now?',
                choices = ('yes', 'no'),
                default = ''
            )

            if to_install == 'no':
                logger.info('Unable to continue until you install "github-markup"')

                return False

            try:
                self._install_github_markup()
            except DepsInstallationFailure as e:
                logger.error(e)
                logger.info('Unable to continue without "github-markup"')

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
