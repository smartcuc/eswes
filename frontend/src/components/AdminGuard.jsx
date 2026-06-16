/*
# src/components/AdminGuard.jsx
*/

export default function AdminGuard({ user, children }) {
    if (!user) return <div>Not logged in</div>;
    if (!user.is_staff) return <div>Access denied</div>;

    return children;
}
