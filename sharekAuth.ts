export interface SharekUser {
    LoginName: string;
    Title: string;
    Email?: string;
    [key: string]: any;
}

// Get currently logged-in Sharek user
export async function getCurrentUser(sharekBaseUrl: string): Promise<SharekUser | null> {
    const url = `${sharekBaseUrl}/_api/Web/currentUser`;

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "accept": "application/json; odata=verbose",
                "content-type": "application/json; odata=verbose"
            },
            credentials: "include" // important for SharePoint auth
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data.d as SharekUser;

    } catch (err) {
        console.error("Failed to get current user:", err);
        return null;
    }
}

// Get detailed user profile info (department, job title, etc.)
export async function getUserDetails(sharekBaseUrl: string, username: string): Promise<any | null> {

    const encodedAccount = encodeURIComponent(`ARAMCO\\${username}`);

    const url = `${sharekBaseUrl}/_api/SP.UserProfiles.PeopleManager/GetPropertiesFor(accountName=@v)?@v='${encodedAccount}'`;

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "accept": "application/json; odata=verbose",
                "content-type": "application/json; odata=verbose"
            },
            credentials: "include"
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        return data.d;

    } catch (err) {
        console.error("Failed to get user details:", err);
        return null;
    }
}

// Check if user is in allowed list
export function isAuthorized(userLogin: string, allowedUsers: string[] = []): boolean {
    return allowedUsers.includes(userLogin.toUpperCase());
}

// Example function to load user and restrict page
export async function authenticateUser(sharekBaseUrl: string, allowedUsers: string[] = []): Promise<SharekUser | false> {

    const user = await getCurrentUser(sharekBaseUrl);

    if (!user) {
        console.info("Could not authenticate with Sharek.");
        return false;
    }

    if (
        allowedUsers.length > 0 &&
        !isAuthorized(user.LoginName, allowedUsers)
    ) {
        console.warn("Access denied: You are not authorized to view this page.");
        return false;
    }

    console.log("Authenticated as Sharek User:", user.Title, user.LoginName);

    return user;
}
