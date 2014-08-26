import os
import platform
import subprocess
import tempfile

SYSTEM = platform.system()
PYOBJC = False

if SYSTEM == 'Darwin':
    try:
        from Foundation import NSDate, NSURL, NSUserNotification, NSUserNotificationCenter
        from AppKit import NSImage
        PYOBJC = True
    except ImportError:
        PYOBJC = False


class Notifier(object):

    def __init__(self):
        self.tempfile_dir = None
        self.notify = None
        self.bin_path = None
        self.notify_available = True

        if SYSTEM == 'Darwin':
            proc = subprocess.Popen(
                ["which", "terminal-notifier"], stdout=subprocess.PIPE)
            env_bin_path = proc.communicate()[0].strip()
            if env_bin_path and os.path.exists(env_bin_path):
                self.bin_path = os.path.realpath(env_bin_path)
                self.notify = self._terminal_notifier_notify
            elif os.path.exists("/usr/local/bin/terminal-notifier"):
                self.bin_path = os.path.join(
                    "/usr/local/bin/", "terminal-notifier")
                self.notify = self._terminal_notifier_notify
            elif PYOBJC:
                self.notify = self._pyobjc_notify
            else:
                self.notify_available = False

        if SYSTEM == "Linux":
            proc = subprocess.Popen(
                ["which", "notify-send"], stdout=subprocess.PIPE)
            env_bin_path = proc.communicate()[0].strip()
            if env_bin_path and os.path.exists(env_bin_path):
                self.bin_path = os.path.realpath(env_bin_path)
                self.notify = self._notify_send_notify
            elif os.path.exists("/usr/bin/notify-send"):
                self.bin_path = os.path.join("/usr/bin/", "notify-send")
                self.notify = self._notify_send_notify
            else:
                self.notify_available = False

        if not self.notify_available:
            print("Notify not available.")
            self.notify = self._notify_not_available

    def _notify_not_available(self, **kwargs):
        return
        
    def _terminal_notifier_notify(self, message, title=None, subtitle=None, appIcon=None, contentImage=None, open_URL=None, delay=0, sound=False):

        args = ['-message', message]
        args += ['-title', title]
        args += ['-subtitle', subtitle]
        args += ['-appIcon', appIcon]
        args += ['-contentImage', contentImage]
        args += ['-open', open_URL]

        args = [str(arg) for arg in args]
        output = subprocess.Popen(
            [self.bin_path, ] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if output.returncode:
            raise Exception("Some error during subprocess call.")

        return output

    def _notify_send_notify(self, message, title=None, subtitle=None, appIcon=None, contentImage=None, open_URL=None, delay=0, sound=False):
        # Download the image
        self.tempfile_dir = tempfile.mkdtemp()
        subprocess.Popen([
            'curl',
            '-o',
            self.tempfile_dir + '/' + str(title.__hash__()) + '.jpg',
            appIcon],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        subprocess.Popen([
            self.bin_path,
            '-i',
            self.tempfile_dir + '/' + str(title.__hash__()) + '.jpg',
            title,
            subtitle],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

    def _pyobjc_notify(self, message, title=None, subtitle=None, appIcon=None, contentImage=None, open_URL=None, delay=0, sound=False):
        notification = NSUserNotification.alloc().init()
        notification.setInformativeText_(message)
        if title:
            notification.setTitle_(title)
        if subtitle:
            notification.setSubtitle_(subtitle)
        if appIcon:
            url = NSURL.alloc().initWithString_(appIcon)
            image = NSImage.alloc().initWithContentsOfURL_(url)
            notification.set_identityImage_(image)
        if contentImage:
            url = NSURL.alloc().initWithString_(contentImage)
            image = NSImage.alloc().initWithContentsOfURL_(url)
            notification.setContentImage_(image)

        if sound:
            notification.setSoundName_("NSUserNotificationDefaultSoundName")
        notification.setDeliveryDate_(
            NSDate.dateWithTimeInterval_sinceDate_(delay, NSDate.date()))
        NSUserNotificationCenter.defaultUserNotificationCenter().scheduleNotification_(
            notification)


Notifier = Notifier()
