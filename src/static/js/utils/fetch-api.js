const API_URL = 'http://localhost:5000/api/v1';

function getAuthHeader() {
    const token = localStorage.getItem('auth_token');
    if (token) {
        return {'Authorization': `Bearer ${token}`};
    }
    return {};
}

async function fetchGet(endpoint, params = {}, useAuth = false) {
    let url = new URL(`${API_URL}${endpoint}`);

    // Change params to string
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

    const headers = useAuth ? getAuthHeader() : {};

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...headers
            }
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch GET failed: ', error);
        throw error;
    }
}

async function fetchPost(endpoint, body = {}, useAuth = false) {
    const headers = {
        'Content-Type': 'application/json',
        ...useAuth ? getAuthHeader() : {}
    };

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(body)
        });

        const data = await response.json();

        return data;
    } catch (error) {
        console.error('Fetch POST failed: ', error);
        throw error;
    }
}

async function fetchPut(endpoint, body = {}, useAuth = false) {
    const headers = {
        'Content-Type': 'application/json',
        ...useAuth ? getAuthHeader() : {}
    };

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'PUT',
            headers: headers,
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch PUT failed: ', error);
        throw error;
    }
}

async function fetchDelete(endpoint, body = {}, useAuth = false) {
    const headers = {
        'Content-Type': 'application/json',
        ...useAuth ? getAuthHeader() : {}
    };

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'DELETE',
            headers: headers,
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch DELETE failed: ', error);
        throw error;
    }
}

async function fetchPatch(endpoint, body = {}, useAuth = false) {
    const headers = {
        'Content-Type': 'application/json',
        ...useAuth ? getAuthHeader() : {}
    };

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'PATCH',
            headers: headers,
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch PATCH failed: ', error);
        throw error;
    }
}
