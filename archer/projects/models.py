import os
import re
import shutil
from django.core import validators
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


def validator_dir_exists(path):
    if not os.path.exists(path):
        raise ValidationError('%s does not exist!' % path, code='dir_not_exist')
    if not os.path.isdir(path):
        raise ValidationError('%s is not a directory!' % path, code='dir_not_dir')
    if not os.access(path, os.W_OK | os.X_OK):
        raise ValidationError('%s is not writable!' % path, code='dir_not_writable')


def validator_relative_path(path):
    rel_path = os.path.relpath(path)
    if re.match('^(\.\./.+|/.+|\.\.)$', rel_path):
        raise ValidationError(_('Directory path name must be relative path beneath the file system.'), code='dir_name')


class FileSystem(models.Model):
    alias = models.CharField(max_length=2000, blank=True, unique=True)
    mount_point = models.CharField(max_length=2000, null=False, blank=False, unique=True,
                                   validators=[validator_dir_exists])

    class Meta:
        permissions = (
            ('setup_filesystem', 'Setup file system'),
        )

    def validate_unique(self, *args, **kwargs):
        """
            Validates if "alias" is unique within scope of "mount_point".
            "alias" mustn't be equal to any other "alias" or "mount_point".
            Same applies to "mount_point" which mustn't equal to any other "alias" except for the same entity.
            """

        def validate_uniqueness_of_alias_and_mount_point(rethrow_error=None):
            uq_mount = self.__class__.objects.filter(
                Q(alias=self.mount_point)
            )
            uq_alias = self.__class__.objects.filter(
                Q(mount_point=self.alias)
            )

            errors = {}
            if not self._state.adding and self.pk is not None:
                uq_mount = uq_mount.exclude(pk=self.pk)
                uq_alias = uq_alias.exclude(pk=self.pk)

            if uq_mount.exists():
                errors['mount_point'] = (
                    'Field is the same as "Alias" for other file system (alias="%s", mount_point="%s")!' % (
                        uq_mount.get().alias, uq_mount.get().mount_point), )
            if uq_alias.exists():
                errors['alias'] = (
                    'Field is the same as "Mount point" for other file system (alias="%s", mount_point="%s")!' % (
                        uq_alias.get().alias, uq_alias.get().mount_point), )
            if len(errors) > 0:
                errors[NON_FIELD_ERRORS] = ('To avoid confusion choose different name!',)
                if rethrow_error is None:
                    rethrow_error = ValidationError(errors)
                else:
                    rethrow_error.message_dict.update(errors)
            if rethrow_error is not None:
                return rethrow_error

        try:
            super(FileSystem, self).validate_unique(*args, **kwargs)
            e = validate_uniqueness_of_alias_and_mount_point()
            if e is not None:
                raise e
        except ValidationError as e:
            raise validate_uniqueness_of_alias_and_mount_point(e)

    def alias_path(self):
        if self.alias is None or len(self.alias) == 0:
            return self.mount_point
        else:
            return self.alias

    @classmethod
    def can_setup(cls, user):
        return user is not None and user.is_superuser and user.is_staff

    def __unicode__(self):
        return self.alias_path()


class Project(models.Model):
    file_system = models.ForeignKey(FileSystem, null=False)
    directory = models.CharField(max_length=200, null=False, blank=False, validators=[validator_relative_path])

    class Meta:
        unique_together = ('file_system', 'directory')
        permissions = (
            ('view_project', 'View project'),
            ('upload_package', 'Upload package'),
            ('deploy_package', 'Deploy package'),
            ('make_directory', 'Make directory'),
            ('remove_directory', 'Remove directory'),
            ('setup_project', 'Setup project'),
        )

    def clean_fields(self, exclude=''):
        path = self.full_path()
        super(Project, self).clean_fields(exclude)

        try:
            validator_dir_exists(path)
        except ValidationError as e:
            raise ValidationError({'directory': (e.messages[0],)})

    def full_path(self):
        return os.path.join(self.file_system.mount_point, self.directory)

    def alias_path(self):
        return os.path.join(self.file_system.alias_path(), self.directory)

    def subdir(self, subdir=''):
        """
        Returns absolute path to subdirectory of `self.directory`.
        Raises ValueError if `subdir` is not a offspring of `self.directory`.
        """
        if subdir is None or len(subdir) == 0:
            return self.full_path()
        if subdir.startswith('/'):
            raise ValueError('Cannot provide root path "%s" as subdir!' % subdir)
        if os.path.normpath(subdir).startswith('..'):
            raise ValueError('Cannot privide a path "%s" pointing to parent directory!' % subdir)
        return os.path.abspath(os.path.join(self.full_path(), subdir))

    def clear_dir(self, subdir=''):
        """
        Removes all files in project's directory.
        """
        if not os.path.isdir(self.file_system.mount_point):
            raise ValueError("mount_point %s is not a directory" % self.file_system.mount_point)
        if not os.path.isdir(self.full_path()):
            raise ValueError("project %s is not a directory" % self.full_path())
        path = self.subdir(subdir)
        if not os.path.isdir(path):
            raise ValueError("%s is not a directory" % path)
        for root, dirs, files in os.walk(path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        return True

    @classmethod
    def can_setup(cls, user):
        return user is not None and user.is_superuser and user.is_staff and FileSystem.objects.count() > 0

    def __unicode__(self):
        return self.alias_path()
