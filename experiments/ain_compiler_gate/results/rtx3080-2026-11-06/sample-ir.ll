; ModuleID = '<string>'
source_filename = "<string>"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc"

; Function Attrs: mustprogress nofree norecurse nosync nounwind readnone willreturn
define i64 @solve(i64 %x) local_unnamed_addr #0 {
entry:
  %.4 = add i64 %x, 6
  ret i64 %.4
}

attributes #0 = { mustprogress nofree norecurse nosync nounwind readnone willreturn }

