"""Use packaged render_docx.py with a Word export adapter on Windows.

The configured Windows runtime does not bundle LibreOffice. This adapter uses a
new hidden Microsoft Word instance, not a user's LibreOffice installation. The
packaged renderer still performs DOCX preparation, PDF rasterization and naming.
"""
from pathlib import Path
import argparse
import importlib.util
import os
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--renderer',type=Path,required=True)
    parser.add_argument('--poppler-bin',type=Path,required=True)
    parser.add_argument('--preexported-pdf',type=Path,
                        help='Optional fresh Word export of this DOCX for rasterization.')
    args=parser.parse_args()
    if sys.platform!='win32': raise SystemExit('Use the ordinary packaged renderer on non-Windows hosts.')
    spec=importlib.util.spec_from_file_location('packaged_docx_renderer',args.renderer)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    shell=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
    def word_export(doc_path,user_profile,convert_tmp_dir,stem,verbose=False):
        if args.preexported_pdf:
            if args.preexported_pdf.stat().st_mtime < args.input.stat().st_mtime:
                return '', 'Pre-exported PDF is older than the DOCX.'
            return str(args.preexported_pdf.resolve()), 'Fresh Microsoft Word export supplied.'
        target=Path(convert_tmp_dir)/(stem+'.pdf')
        literal=lambda value:"'"+str(value).replace("'","''")+"'"
        # Native COM commands; no execution-policy changes or unsigned script loading.
        command=("$w=New-Object -ComObject Word.Application; $d=$null; try { "
                 "$w.Visible=$false; $w.DisplayAlerts=0; $w.AutomationSecurity=3; "
                 "$d=$w.Documents.Open("+literal(Path(doc_path).resolve())+",$false,$true); "
                 "$d.Repaginate(); $d.Fields.Update() | Out-Null; "
                 "$d.ExportAsFixedFormat("+literal(target.resolve())+",17) "
                 "} finally { if($null -ne $d){$d.Close(0); "
                 "[System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($d)|Out-Null}; "
                 "$w.Quit();[System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($w)|Out-Null }")
        result=subprocess.run([str(shell),'-NoProfile','-NonInteractive','-Command',command],
                              capture_output=True,text=True,timeout=150)
        logs=result.stdout+result.stderr
        if result.returncode or not target.is_file(): return '',logs
        return str(target),logs
    module.convert_to_pdf=word_export
    os.environ['PATH']=str(args.poppler_bin)+os.pathsep+os.environ.get('PATH','')
    sys.argv=[str(args.renderer),str(args.input),'--output_dir',str(args.output),'--emit_pdf','--dpi','140']
    module.main()


if __name__=='__main__': main()
