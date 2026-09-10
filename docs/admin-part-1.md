# Administration — Part 1

The administration portal is read-only and aggregate-only. It reuses existing login, token storage, current-user resolution, and the authenticated Axios client. No administrator credentials appear in source or documentation.

## Authorization and routing

`GET /api/v1/admin/overview` is protected at the admin router by `require_admin`, which calls the existing current-user dependency. Missing, invalid, expired, and inactive sessions receive 401. A current database role of USER receives 403; ADMIN and SUPER_ADMIN are allowed. JWT role claims alone do not grant access.

Login sends ADMIN/SUPER_ADMIN to `/admin/dashboard`. USER retains a safe local return destination or `/dashboard`. The admin guard waits for session restoration and redirects USER to `/dashboard`. Entrepreneur routes send officers back to their own dashboard. `UserDashboardLayout` and its navigation configuration are unchanged.

`AdminDashboardLayout` has dedicated dashboard/logout navigation and an officer identity badge. Future modules are described as coming soon, without links to fake pages. On smaller screens the menu expands inline; no modal focus trap is needed. It includes an accessible toggle, semantic navigation, skip link, focus styles, and responsive KPI cards.

## KPI contract

The endpoint calls `AdminService`, then `AdminRepository`, which runs one PostgreSQL aggregate query. The profile's unique `user_id` prevents double counting in the left join.

| Response field | Definition |
| --- | --- |
| total_registered_users | All accounts with role USER, including inactive accounts |
| total_entrepreneurs | USER accounts with an entrepreneur_profiles row, regardless of onboarding completion |
| profiles_pending | USER accounts without a profile row; not incomplete onboarding |
| new_enterprises | USER profiles with has_existing_business = false |
| existing_enterprises | USER profiles with has_existing_business = true |
| states_count | Distinct nonblank states on USER profiles |
| districts_count | Distinct state/district pairs where both are nonblank on USER profiles |

Null enterprise status contributes to neither new nor existing. Location comparisons collapse whitespace, trim, and lowercase without updating stored values. Missing locations are excluded; nothing is inferred. Admin/SUPER_ADMIN accounts and their profiles contribute to no KPI. Response fields are seven nonnegative integers, with no personal data.

The frontend renders those returned values directly. Skeletons replace numbers during loading; errors never display raw server details. A 401 clears the session and redirects to login. A 403 displays the permission message. Zero users and users without profiles have different empty messages. Admin text uses the existing EN/HI/MR message lookup.

## Local verification

1. Start the backend using its existing environment: `cd backend`, activate `.venv`, then `uvicorn app.main:app --reload`.
2. From the project root run `npm run dev`.
3. Log in with the locally configured officer account. Expect `/admin/dashboard`, seven real totals, and officer-only navigation.
4. Refresh after a legitimate registration/profile change to fetch current totals.
5. Use the language selector to check English, Hindi, and Marathi. Resize below 900px and test the menu by keyboard; check narrow-screen cards and focus indicators.
6. Log out and log in with an existing entrepreneur. Expect the existing entrepreneur destination. Visiting `/admin/dashboard` must redirect to `/dashboard`.
7. Verify the API with authenticated requests: USER receives 403; ADMIN/SUPER_ADMIN receive 200; no token receives 401. Do not paste tokens into documentation or logs.
8. In TablePlus compare USER counts and USER-joined profile counts with the definitions above. Do not count officer accounts or change data to populate cards.

Automated coverage includes backend authorization, changed database roles, inactive accounts, exact aggregates, missing locations, duplicate location casing, empty aggregates, and the response allowlist. Frontend tests cover guard rendering, destination selection, shared-client fetching, values, loading/empty/error states, languages, and separate navigation. Static-render tests do not replace interactive browser verification.

No migrations, dependencies, geographic drill-downs, entrepreneur records, charts, editing, or Part 2 features are included.

## Validation results

- Targeted backend admin/auth/bootstrap: 31 passed.
- Full backend: 442 passed, 17 failed. An isolated unchanged HEAD run reproduced the same 17 failures (421 passed), in business analysis, Google nearby, and nearby market tests.
- Frontend: 102 passed, including 15 admin tests.
- Python compilation, lint, production build, and `git diff --check`: passed. Compilation used a writable temporary cache directory because the macOS default cache is outside the sandbox.
- Build retains a warning about the large main JavaScript chunk; no dependencies were added.
- Local officer login and overview returned 200. Independent PostgreSQL queries matched all seven totals: 9 registered users, 6 profiles, 3 pending, 5 new, 1 existing, 1 state, 6 districts at verification time.
- Interactive browser checks were not run; no browser automation runtime is available in this workspace. Follow the steps above for visual and interactive acceptance.

Files added for Part 1: backend admin endpoint, repository, response schema, service, and test; frontend AdminDashboardPage, admin CSS, AdminDashboardLayout, AdminProtectedRoute, roleRouting helper, adminService, admin tests, and this document.

Existing files changed for Part 1: backend API dependencies and v1 router; frontend AppRouter, ProtectedRoute, LoginPage, and i18n messages. Earlier bootstrap/config/environment changes were preserved.
