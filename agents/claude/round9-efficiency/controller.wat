(module
  (import "env" "log_t0" (func $log_t0 (param i32)))
  (import "env" "log_t1" (func $log_t1 (param i32 i32)))
  (func (export "main") (param $n i32) (local $i i32)
    (block $done
      (loop $next
        (br_if $done (i32.ge_s (local.get $i) (local.get $n)))
        (if (i32.eqz (local.get $i))
          (then (call $log_t0 (local.get $n)))
          (else (call $log_t1 (i32.add (local.get $i) (i32.const 1)) (local.get $n))))
        (local.set $i (i32.add (local.get $i) (i32.const 1)))
        (br $next)))))
