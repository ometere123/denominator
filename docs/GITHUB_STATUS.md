# GitHub and release status

Repository: https://github.com/ometere123/denominator

The historical baseline was `6a10889611e169a80492fc71e96499d30d1b5dd2`.
The current release work adds strict duplicate-key rejection, explicit web
response validation, true Keccak test vectors, native Direct Mode validator
regressions, a focused mutation check, the repository-local CLI lockfile,
stable direct-RPC guarding, and CI jobs for Direct Mode and GenVM validation.

The final tested contract/evidence source commit is
`7a2240c69b451ac39d9ede5bd71fdaf10f6097b7` on `main`. GitHub Actions run
`https://github.com/ometere123/denominator/actions/runs/44049720163` completed
successfully for that exact commit. Ubuntu baseline, Windows baseline, Direct
Mode and GenVM lint jobs all passed. This status-file amendment is
documentation-only and does not change either contract source; the final branch
head and its follow-up CI run are recorded in the release report. Earlier
workflows remain historical and are not treated as proof for this source.
