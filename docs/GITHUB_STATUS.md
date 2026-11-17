# GitHub and release status

Repository: https://github.com/ometere123/denominator

The historical baseline was `6a10889611e169a80492fc71e96499d30d1b5dd2`.
The current release work adds strict duplicate-key rejection, explicit web
response validation, true Keccak test vectors, native Direct Mode validator
regressions, a focused mutation check, the repository-local CLI lockfile,
stable direct-RPC guarding, and CI jobs for Direct Mode and GenVM validation.

The final tested contract source commit is
`7a2240c69b451ac39d9ede5bd71fdaf10f6097b7` on `main`. GitHub Actions run
`https://github.com/ometere123/denominator/actions/runs/44049720163` completed
successfully for that exact contract source. Ubuntu baseline, Windows baseline,
Direct Mode and GenVM lint jobs all passed. Later commits update only release
documentation and controlled live fixtures; they do not change either deployed
contract source. The current-primary lifecycle receipts are recorded in
`docs/live-evidence.json`, and the branch-head CI result is recorded in the
final release report. Earlier workflows remain historical and are not treated
as proof for a different source.
