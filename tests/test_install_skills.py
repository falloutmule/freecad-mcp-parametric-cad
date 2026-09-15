import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import install_skills as installer


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='companion-installer-')
        self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.repo=self.base/'repo'
        self.skills=self.base/'skills'
        self.backups=self.base/'backups'
        for d in (self.repo,self.skills,self.backups): d.mkdir()
        self.core='freecad-mcp-parametric-cad'
        self.companion='blockfolk-figure-design'
        self.write(self.repo/'SKILL.md',f'---\nname: {self.core}\ndescription: Generic CAD\n---\n')
        self.write(self.repo/'scripts/fcskill/__init__.py','VERSION="2.1.0.dev1"\n')
        self.write(self.repo/'skills/blockfolk/SKILL.md',f'---\nname: {self.companion}\ndescription: Blockfolk figures\n---\n')
        self.write(self.repo/'skills/blockfolk/scripts/helper.py','VALUE=1\n')
        self.catalog={'schema_version':1,'packages':{
          'core':{'name':self.core,'source':'.','include':['SKILL.md','scripts']},
          'blockfolk':{'name':self.companion,'source':'skills/blockfolk','include':['SKILL.md','scripts'],'requires':self.core}}}
        self.write(self.repo/'skill-packages.json',json.dumps(self.catalog))

    def write(self,p,text):
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(text,encoding='utf-8')

    def install(self,selection='all',baseline=None):
        return installer.install(self.repo,selection,self.skills,self.backups,baseline)

    def test_core_only_excludes_companion(self):
        self.install('core')
        self.assertEqual(installer.identity(self.skills/self.core),self.core)
        self.assertFalse((self.skills/self.companion).exists())
        self.assertFalse((self.skills/self.core/'skills').exists())

    def test_blockfolk_requires_dependency(self):
        with self.assertRaises(installer.InstallError): self.install('blockfolk')
        self.assertEqual(list(self.skills.iterdir()),[])

    def test_blockfolk_only_preserves_core(self):
        self.install('core')
        before=installer.snapshot(self.skills/self.core)
        self.install('blockfolk')
        self.assertEqual(before,installer.snapshot(self.skills/self.core))

    def test_all_has_two_peer_entrypoints(self):
        self.install()
        found={installer.identity(p.parent) for p in self.skills.glob('*/SKILL.md')}
        self.assertEqual(found,{self.core,self.companion})

    def test_dry_run_makes_no_changes(self):
        result=installer.plan_install(self.repo,'all',self.skills)
        self.assertEqual(result['status'],'DRY_RUN')
        self.assertEqual(list(self.skills.iterdir()),[])
        self.assertEqual(list(self.backups.iterdir()),[])

    def test_idempotent_install(self):
        self.install()
        before=list(self.backups.iterdir())
        self.assertEqual(self.install()['status'],'ALREADY_INSTALLED')
        self.assertEqual(list(self.backups.iterdir()),before)

    def test_local_modified_file_refused(self):
        self.install()
        self.write(self.skills/self.companion/'scripts/helper.py','local edit')
        with self.assertRaises(installer.InstallError): self.install()
        self.assertEqual((self.skills/self.companion/'scripts/helper.py').read_text(),'local edit')

    def test_local_extra_file_refused(self):
        self.install()
        self.write(self.skills/self.companion/'notes.txt','user notes')
        with self.assertRaises(installer.InstallError): self.install()

    def test_missing_file_refused(self):
        self.install()
        (self.skills/self.companion/'scripts/helper.py').unlink()
        with self.assertRaises(installer.InstallError): self.install()

    def test_managed_update_and_exact_rollback(self):
        self.install()
        before=installer.snapshot(self.skills/self.companion)
        self.write(self.repo/'skills/blockfolk/scripts/helper.py','VALUE=2\n')
        result=self.install('blockfolk')
        receipt=Path(result['backup_directory'])/'receipt.json'
        self.assertEqual(installer.rollback(receipt)['status'],'ROLLBACK_DRY_RUN')
        self.assertNotEqual(before,installer.snapshot(self.skills/self.companion))
        installer.rollback(receipt,apply=True)
        self.assertEqual(before,installer.snapshot(self.skills/self.companion))

    def test_new_install_rollback_preserves_removed_version(self):
        result=self.install()
        txn=Path(result['backup_directory'])
        installer.rollback(txn/'receipt.json',apply=True)
        self.assertFalse((self.skills/self.core).exists())
        self.assertTrue((txn/'rolled-back'/self.core/'SKILL.md').exists())

    def test_rollback_refuses_later_edit(self):
        result=self.install()
        self.write(self.skills/self.core/'SKILL.md','user edit')
        with self.assertRaises(installer.InstallError): installer.rollback(Path(result['backup_directory'])/'receipt.json',True)

    def test_known_baseline_adoption_preserves_exact_original(self):
        self.install('core')
        baseline=self.base/'baseline'
        old=baseline/self.companion
        self.write(old/'SKILL.md',f'---\nname: {self.companion}\ndescription: Old package\n---\n')
        self.write(old/'private-reference.bin','private local reference')
        shutil.copytree(old,self.skills/self.companion)
        before=installer.snapshot(old)
        with self.assertRaises(installer.InstallError): self.install('blockfolk')
        result=self.install('blockfolk',baseline)
        self.assertEqual(before,installer.snapshot(Path(result['backup_directory'])/'before'/self.companion))

    def test_baseline_does_not_override_divergence(self):
        self.install('core')
        baseline=self.base/'baseline'
        old=baseline/self.companion
        shutil.copytree(self.repo/'skills/blockfolk',old)
        shutil.copytree(old,self.skills/self.companion)
        self.write(self.skills/self.companion/'scripts/helper.py','user edit')
        with self.assertRaises(installer.InstallError): self.install('blockfolk',baseline)

    def test_wrong_identity_refused(self):
        self.write(self.skills/self.core/'SKILL.md','---\nname: unrelated\ndescription: Test\n---\n')
        with self.assertRaises(installer.InstallError): self.install('core')

    def test_file_destination_refused(self):
        self.write(self.skills/self.core,'not a folder')
        with self.assertRaises(installer.InstallError): self.install('core')

    def test_git_checkout_destination_refused(self):
        self.write(self.skills/self.core/'.git','gitdir: elsewhere')
        with self.assertRaises(installer.InstallError): self.install('core')

    def test_second_publication_failure_rolls_back_first(self):
        self.install()
        before={n:installer.snapshot(self.skills/n) for n in (self.core,self.companion)}
        self.write(self.repo/'scripts/fcskill/__init__.py','VERSION="changed"\n')
        self.write(self.repo/'skills/blockfolk/scripts/helper.py','VALUE=2\n')
        real=installer._publish_directory
        calls=[]
        def fail_second(stage,target):
            calls.append(target.name)
            if len(calls)==2: raise OSError('injected second publish failure')
            return real(stage,target)
        with patch.object(installer,'_publish_directory',side_effect=fail_second):
            with self.assertRaises(OSError): self.install()
        self.assertEqual(len(calls),2)
        self.assertEqual(before,{n:installer.snapshot(self.skills/n) for n in before})

    def test_existing_lock_preserved(self):
        lock=self.skills/'.fcskill-install.lock'
        lock.write_text('another writer')
        with self.assertRaises(FileExistsError): self.install()
        self.assertEqual(lock.read_text(),'another writer')

    def test_backup_inside_discovery_refused(self):
        inside=self.skills/'backups'
        inside.mkdir()
        with self.assertRaises(installer.InstallError): installer.install(self.repo,'core',self.skills,inside)

    def test_traversal_payload_refused(self):
        self.catalog['packages']['core']['include'].append('../secret')
        self.write(self.repo/'skill-packages.json',json.dumps(self.catalog))
        with self.assertRaises(installer.InstallError): self.install()

    def test_rollback_refuses_tampered_backup(self):
        self.install()
        self.write(self.repo/'skills/blockfolk/scripts/helper.py','VALUE=2\n')
        result=self.install('blockfolk')
        txn=Path(result['backup_directory'])
        self.write(txn/'before'/self.companion/'scripts/helper.py','tampered')
        with self.assertRaises(installer.InstallError): installer.rollback(txn/'receipt.json',True)

    def test_real_catalog_keeps_core_runtime_independent(self):
        catalog=json.loads((ROOT/'skill-packages.json').read_text())
        core=installer.payload(ROOT,catalog['packages']['core'])
        self.assertIn('scripts/fcskill/__init__.py',core)
        self.assertFalse(any(p.startswith('skills/') or 'blockfolk' in p for p in core))

    def test_duplicate_peer_names_refused(self):
        self.catalog['packages']['blockfolk']['name']=self.core
        self.write(self.repo/'skill-packages.json',json.dumps(self.catalog))
        with self.assertRaises(installer.InstallError): self.install()
        self.assertEqual(list(self.skills.iterdir()),[])

    def test_partial_manual_rollback_recovers_installed_state(self):
        self.install()
        self.write(self.repo/'scripts/fcskill/__init__.py','VERSION="changed"\n')
        self.write(self.repo/'skills/blockfolk/scripts/helper.py','VALUE=2\n')
        result=self.install()
        before={n:installer.snapshot(self.skills/n) for n in (self.core,self.companion)}
        txn=Path(result['backup_directory'])
        real=installer.os.replace
        injected=[]
        def fail_one_restore(src,dst):
            if Path(src)==txn/'before'/self.core and not injected:
                injected.append(True)
                raise OSError('injected restore failure')
            return real(src,dst)
        with patch.object(installer.os,'replace',side_effect=fail_one_restore):
            with self.assertRaises(OSError): installer.rollback(txn/'receipt.json',True)
        self.assertTrue(injected)
        self.assertEqual(before,{n:installer.snapshot(self.skills/n) for n in before})
        self.assertEqual(installer.rollback(txn/'receipt.json',True)['status'],'ROLLED_BACK')


if __name__=='__main__': unittest.main()
