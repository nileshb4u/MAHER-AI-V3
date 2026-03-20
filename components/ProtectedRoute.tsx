import React from 'react';
import { useAuth } from './AuthProvider';

interface ProtectedRouteProps {
    children: React.ReactNode;
    requireAdmin?: boolean;
    fallback?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    requireAdmin = false,
    fallback = null,
}) => {
    const { isAdmin, isGuest } = useAuth();

    if (requireAdmin && !isAdmin) {
        return <>{fallback}</>;
    }

    return <>{children}</>;
};

interface AdminOnlyProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
}

export const AdminOnly: React.FC<AdminOnlyProps> = ({ children, fallback = null }) => {
    const { isAdmin } = useAuth();

    if (!isAdmin) {
        return <>{fallback}</>;
    }

    return <>{children}</>;
};

interface GuestOnlyProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
}

export const GuestOnly: React.FC<GuestOnlyProps> = ({ children, fallback = null }) => {
    const { isGuest } = useAuth();

    if (!isGuest) {
        return <>{fallback}</>;
    }

    return <>{children}</>;
};
