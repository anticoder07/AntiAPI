import {truncateText} from '../utils/helpers.js';

let sidebarInstance = null;
let currentApiDetails = null;

async function loadProject() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const pid = urlParams.get('id');
        if (pid === null)
            return null;

        const msg = await fetchGet('/projects/single', {"id": pid}, true);

        if (msg.status === 'SUCCESS') {
            return msg.data;
        } else {
            Notification.show(msg.message, 'error');
            return null;
        }
    } catch (error) {
        console.error('Error fetching project list:', error);
        Notification.show('An error occurred while fetching project list', 'error');
        return null;
    }
}

async function loadTopicList() {
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const pid = urlParams.get('id');
        if (pid === null)
            return;

        // First load the project to get the project name
        const project = await loadProject();
        const projectName = project ? project.project_name : "Loading Project...";

        // Then load the topics
        const msg = await fetchGet('/topics', {"pid": pid}, true);

        if (msg.status === 'SUCCESS') {
            if (sidebarInstance) {
                sidebarInstance.updateSideBarData(projectName, msg);
            }
        } else {
            Notification.show(msg.message, 'error');
        }
    } catch (error) {
        console.error('Error fetching project list:', error);
        Notification.show('An error occurred while fetching project list', 'error');
    }
}

async function loadApiList(topic_id) {
    try {
        const msg = await fetchGet('/apis', {"tid": topic_id}, true);

        if (msg.status === 'SUCCESS') {
            // Update the sidebar with the API data
            if (sidebarInstance) {
                sidebarInstance.updateTopicApis(topic_id, msg);
            }
        } else {
            Notification.show(msg.message, 'error');
        }
    } catch (error) {
        console.error('Error fetching API list:', error);
        Notification.show('An error occurred while fetching API list', 'error');
    }
}

async function loadApiContent(api) {
    currentApiDetails = api;

    try {
        const mainContent = document.querySelector('.main-content');
        if (!mainContent) return;

        const apiPageHTML = `
            <div class="flex flex-col h-screen" style="background-color: var(--background-color); color: var(--text-color);">
                <header class="app-header-container flex justify-between items-center px-4 py-3 sticky top-0 z-10 bg-transparent backdrop-blur-md">
                    <div class="flex items-center">
                        <div class="mr-4 relative">
                            <select id="api-method" class="font-semibold py-1 px-2 rounded-md text-base appearance-none cursor-pointer pr-9"
                                    style="background-color: var(--input-bg); border: 1px solid var(--input-border);">
                                <option value="GET" class="api-get font-bold" ${api.protocol === 'GET' ? 'selected' : ''}>GET</option>
                                <option value="POST" class="api-post font-bold" ${api.protocol === 'POST' ? 'selected' : ''}>POST</option>
                                <option value="PUT" class="api-put font-bold" ${api.protocol === 'PUT' ? 'selected' : ''}>PUT</option>
                                <option value="DELETE" class="api-delete font-bold" ${api.protocol === 'DELETE' ? 'selected' : ''}>DELETE</option>
                                <option value="PATCH" class="api-patch font-bold" ${api.protocol === 'PATCH' ? 'selected' : ''}>PATCH</option>
                            </select>
                            <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2"
                                style="color: var(--text-color);">
                                <svg class="fill-current h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                                    <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                                </svg>
                            </div>
                        </div>
                        <span id="api-endpoint" class="editable-url text-lg font-semibold cursor-text px-2 py-1 rounded hover:bg-opacity-10 hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            ondblclick="this.contentEditable=true; this.focus();"
                            onblur="this.contentEditable=false;">
                            ${api.endpoint || 'project/topic/api'}
                        </span>
                    </div>
                    <button id="save-api" class="font-medium rounded-md px-6 py-1 transition-colors duration-200 hover:opacity-90"
                            style="background-color: var(--api-${api.protocol.toLowerCase()}); color: white;">
                        Save
                    </button>
                </header>

                <div class="flex flex-1 overflow-hidden">
                    <div class="w-1/2 p-5 border-r custom-scrollbar overflow-auto" style="border-color: var(--sidebar-border);">
                        <h2 class="text-xl font-medium mb-3">Input</h2>
                        <textarea id="api-input"
                                class="w-full h-5/6 p-4 rounded-md resize-none shadow-inner text-base focus:outline-none focus:ring-2 focus:ring-blue-500"
                                style="background-color: var(--input-bg); border: 1px solid var(--input-border); color: var(--text-color); min-height: calc(100vh - 170px);"
                                placeholder="Enter your input here...">${api.format || ''}</textarea>
                    </div>
                    <div class="w-1/2 p-5 custom-scrollbar overflow-auto">
                        <h2 class="text-xl font-medium mb-3">Preview</h2>
                        <div class="w-full h-5/6 p-4 border rounded-md shadow-sm"
                            style="background-color: var(--popup-bg); border: 1px solid var(--popup-border); min-height: calc(100vh - 170px);">
                            <div id="display-content" class="overflow-auto h-full">
                                <p style="color: var(--text-color);">Your content will appear here...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        mainContent.innerHTML = apiPageHTML;

        setupApiPageListeners();
    } catch (error) {
        Notification.show('An error occurred while loading API content', 'error');
    }
}

function setupApiPageListeners() {
    const saveButton = document.getElementById('save-api');
    if (saveButton) {
        saveButton.addEventListener('click', () => {
            saveApiChanges();
        });
    }

    const methodSelect = document.getElementById('api-method');
    if (methodSelect) {
        methodSelect.addEventListener('change', (e) => {
            const method = e.target.value;
            saveButton.style.backgroundColor = `var(--api-${method.toLowerCase()})`;
        });
    }
}

// Save API changes
async function saveApiChanges() {
    if (!currentApiDetails) return;

    try {
        const method = document.getElementById('api-method').value;
        const endpoint = document.getElementById('api-endpoint').textContent.trim();
        const input = document.getElementById('api-input').value;

        currentApiDetails.protocol = method;
        currentApiDetails.endpoint = endpoint;
        currentApiDetails.format = input;

        const updateData = {
            api_id: currentApiDetails.api_id,
            api_type: method,
            endpoint: endpoint,
            format_api: input
        };

        const response = await fetchPost('/apis/update', updateData, true);

        if (response.status === 'SUCCESS') {
            Notification.show('API updated successfully', 'success');

            // Update sidebar data if needed
            if (sidebarInstance) {
                // Find the topic containing this API
                const topic = sidebarInstance.sideBarData.find(item =>
                    item.type === "topic" && item.apis &&
                    item.apis.some(api => api.api_id === currentApiDetails.api_id)
                );

                if (topic) {
                    // Reload the APIs for this topic to ensure sidebar is updated
                    loadApiList(topic.topic_id);
                }
            }
        } else {
            Notification.show(response.message || 'Failed to update API', 'error');
        }
    } catch (error) {
        console.error('Error saving API changes:', error);
        Notification.show('An error occurred while saving changes', 'error');
    }
}

// Function to show the context menu
function showContextMenu(e, menuItems) {
    e.preventDefault();
    e.stopPropagation();

    // Remove any existing context menus
    hideContextMenu();

    // Create context menu
    const contextMenu = document.createElement('div');
    contextMenu.id = 'context-menu';
    contextMenu.className = 'absolute z-50 bg-white dark:bg-gray-800 shadow-lg rounded-md py-1 min-w-40 text-sm';
    contextMenu.style.left = `${e.pageX}px`;
    contextMenu.style.top = `${e.pageY}px`;

    // Add menu items
    menuItems.forEach(item => {
        const menuItem = document.createElement('div');
        menuItem.className = 'px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer flex items-center';

        // Add icon if provided
        if (item.icon) {
            menuItem.innerHTML = `<i class="${item.icon} mr-2"></i> ${item.label}`;
        } else {
            menuItem.textContent = item.label;
        }

        // Add click handler
        menuItem.addEventListener('click', () => {
            item.action();
            hideContextMenu();
        });

        contextMenu.appendChild(menuItem);
    });

    // Add to DOM
    document.body.appendChild(contextMenu);

    // Add click listener to document to close menu when clicking outside
    setTimeout(() => {
        document.addEventListener('click', hideContextMenu);
    }, 0);
}

// Function to hide the context menu
function hideContextMenu() {
    const existingMenu = document.getElementById('context-menu');
    if (existingMenu) {
        existingMenu.remove();
        document.removeEventListener('click', hideContextMenu);
    }
}

// Handle project rename
async function renameProject(projectId, currentName) {
    // Create modal for renaming
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96">
            <h3 class="text-lg font-medium mb-4">Rename Project</h3>
            <input type="text" id="project-name-input" class="w-full p-2 border rounded-md mb-4" 
                   value="${currentName}" placeholder="Project name">
            <div class="flex justify-end space-x-2">
                <button id="cancel-rename" class="px-4 py-2 border rounded-md">Cancel</button>
                <button id="confirm-rename" class="px-4 py-2 bg-blue-500 text-white rounded-md">Save</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Set up event listeners
    document.getElementById('cancel-rename').addEventListener('click', () => {
        modal.remove();
    });

    document.getElementById('confirm-rename').addEventListener('click', async () => {
        const newName = document.getElementById('project-name-input').value.trim();
        if (newName) {
            try {
                const response = await fetchPost('/projects/update', {
                    id: projectId,
                    project_name: newName
                }, true);

                if (response.status === 'SUCCESS') {
                    Notification.show('Project renamed successfully', 'success');
                    // Update sidebar data
                    loadTopicList();
                } else {
                    Notification.show(response.message || 'Failed to rename project', 'error');
                }
            } catch (error) {
                console.error('Error renaming project:', error);
                Notification.show('An error occurred while renaming project', 'error');
            }
        }
        modal.remove();
    });
}

// Handle project delete
async function deleteProject(projectId) {
    // Create confirmation modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96">
            <h3 class="text-lg font-medium mb-4">Delete Project</h3>
            <p class="mb-4">Are you sure you want to delete this project? This action cannot be undone.</p>
            <div class="flex justify-end space-x-2">
                <button id="cancel-delete" class="px-4 py-2 border rounded-md">Cancel</button>
                <button id="confirm-delete" class="px-4 py-2 bg-red-500 text-white rounded-md">Delete</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Set up event listeners
    document.getElementById('cancel-delete').addEventListener('click', () => {
        modal.remove();
    });

    document.getElementById('confirm-delete').addEventListener('click', async () => {
        try {
            const response = await fetchPost('/projects/delete', {
                id: projectId
            }, true);

            if (response.status === 'SUCCESS') {
                Notification.show('Project deleted successfully', 'success');
                // Redirect to projects list
                window.location.href = '/projects';
            } else {
                Notification.show(response.message || 'Failed to delete project', 'error');
            }
        } catch (error) {
            console.error('Error deleting project:', error);
            Notification.show('An error occurred while deleting project', 'error');
        }
        modal.remove();
    });
}

// Handle topic rename
async function renameTopic(topicId, currentName) {
    // Create modal for renaming
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96">
            <h3 class="text-lg font-medium mb-4">Rename Topic</h3>
            <input type="text" id="topic-name-input" class="w-full p-2 border rounded-md mb-4" 
                   value="${currentName}" placeholder="Topic name">
            <div class="flex justify-end space-x-2">
                <button id="cancel-rename" class="px-4 py-2 border rounded-md">Cancel</button>
                <button id="confirm-rename" class="px-4 py-2 bg-blue-500 text-white rounded-md">Save</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Set up event listeners
    document.getElementById('cancel-rename').addEventListener('click', () => {
        modal.remove();
    });

    document.getElementById('confirm-rename').addEventListener('click', async () => {
        const newName = document.getElementById('topic-name-input').value.trim();
        if (newName) {
            try {
                const response = await fetchPost('/topics/update', {
                    topic_id: topicId,
                    topic_name: newName
                }, true);

                if (response.status === 'SUCCESS') {
                    Notification.show('Topic renamed successfully', 'success');
                    // Update sidebar data
                    loadTopicList();
                } else {
                    Notification.show(response.message || 'Failed to rename topic', 'error');
                }
            } catch (error) {
                console.error('Error renaming topic:', error);
                Notification.show('An error occurred while renaming topic', 'error');
            }
        }
        modal.remove();
    });
}

// Handle topic delete
async function deleteTopic(topicId) {
    // Create confirmation modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96">
            <h3 class="text-lg font-medium mb-4">Delete Topic</h3>
            <p class="mb-4">Are you sure you want to delete this topic? All APIs within this topic will also be deleted.</p>
            <div class="flex justify-end space-x-2">
                <button id="cancel-delete" class="px-4 py-2 border rounded-md">Cancel</button>
                <button id="confirm-delete" class="px-4 py-2 bg-red-500 text-white rounded-md">Delete</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Set up event listeners
    document.getElementById('cancel-delete').addEventListener('click', () => {
        modal.remove();
    });

    document.getElementById('confirm-delete').addEventListener('click', async () => {
        try {
            const response = await fetchPost('/topics/delete', {
                topic_id: topicId
            }, true);

            if (response.status === 'SUCCESS') {
                Notification.show('Topic deleted successfully', 'success');
                // Update sidebar data
                loadTopicList();
            } else {
                Notification.show(response.message || 'Failed to delete topic', 'error');
            }
        } catch (error) {
            console.error('Error deleting topic:', error);
            Notification.show('An error occurred while deleting topic', 'error');
        }
        modal.remove();
    });
}

// Handle API rename
async function renameApi(apiId, currentName) {
    // Create modal for renaming
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96">
            <h3 class="text-lg font-medium mb-4">Rename API</h3>
            <input type="text" id="api-name-input" class="w-full p-2 border rounded-md mb-4" 
                   value="${currentName}" placeholder="API name">
            <div class="flex justify-end space-x-2">
                <button id="cancel-rename" class="px-4 py-2 border rounded-md">Cancel</button>
                <button id="confirm-rename" class="px-4 py-2 bg-blue-500 text-white rounded-md">Save</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Set up event listeners
    document.getElementById('cancel-rename').addEventListener('click', () => {
        modal.remove();
    });

    document.getElementById('confirm-rename').addEventListener('click', async () => {
        const newName = document.getElementById('api-name-input').value.trim();
        if (newName) {
            try {
                const response = await fetchPost('/apis/update', {
                    api_id: apiId,
                    api_name: newName
                }, true);

                if (response.status === 'SUCCESS') {
                    Notification.show('API renamed successfully', 'success');

                    // Find the topic containing this API
                    const topic = sidebarInstance.sideBarData.find(item =>
                        item.type === "topic" && item.apis &&
                        item.apis.some(api => api.api_id === apiId)
                    );

                    if (topic) {
                        // Reload the APIs for this topic
                        loadApiList(topic.topic_id);
                    }
                } else {
                    Notification.show(response.message || 'Failed to rename API', 'error');
                }
            } catch (error) {
                console.error('Error renaming API:', error);
                Notification.show('An error occurred while renaming API', 'error');
            }
        }
        modal.remove();
    });
}

// Handle API delete
async function deleteApi(apiId) {
    // Create confirmation modal
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-96">
            <h3 class="text-lg font-medium mb-4">Delete API</h3>
            <p class="mb-4">Are you sure you want to delete this API?</p>
            <div class="flex justify-end space-x-2">
                <button id="cancel-delete" class="px-4 py-2 border rounded-md">Cancel</button>
                <button id="confirm-delete" class="px-4 py-2 bg-red-500 text-white rounded-md">Delete</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Set up event listeners
    document.getElementById('cancel-delete').addEventListener('click', () => {
        modal.remove();
    });

    document.getElementById('confirm-delete').addEventListener('click', async () => {
        try {
            const response = await fetchPost('/apis/delete', {
                api_id: apiId
            }, true);

            if (response.status === 'SUCCESS') {
                Notification.show('API deleted successfully', 'success');

                // Find the topic containing this API
                const topic = sidebarInstance.sideBarData.find(item =>
                    item.type === "topic" && item.apis &&
                    item.apis.some(api => api.api_id === apiId)
                );

                if (topic) {
                    // Reload the APIs for this topic
                    loadApiList(topic.topic_id);
                }

                // If current API is being displayed, clear the main content
                if (currentApiDetails && currentApiDetails.api_id === apiId) {
                    const mainContent = document.querySelector('.main-content');
                    if (mainContent) {
                        mainContent.innerHTML = '<div class="flex items-center justify-center h-full"><p>Select an API to view its details</p></div>';
                    }
                    currentApiDetails = null;
                }
            } else {
                Notification.show(response.message || 'Failed to delete API', 'error');
            }
        } catch (error) {
            console.error('Error deleting API:', error);
            Notification.show('An error occurred while deleting API', 'error');
        }
        modal.remove();
    });
}

class Sidebar {
    constructor() {
        this.sidebarNav = document.getElementById('sidebar-nav');
        if (!this.sidebarNav) return;

        // Set default data
        this.sideBarData = [
            {
                type: "project",
                content: "Loading Project..."
            }
        ];

        // Store the instance in the module-level variable
        sidebarInstance = this;

        // Add global CSS for context menu
        this.addContextMenuStyles();

        // Render initial state
        this.render();

        // Load project data and topic list
        loadTopicList();
    }

    // Add CSS for context menu
    addContextMenuStyles() {
        const style = document.createElement('style');
        style.textContent = `
            #context-menu {
                border: 1px solid var(--popup-border);
                background-color: var(--popup-bg);
                color: var(--text-color);
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            #context-menu div {
                color: var(--text-color);
            }
            #context-menu div:hover {
                background-color: var(--hover-bg);
            }
        `;
        document.head.appendChild(style);
    }

    updateSideBarData(projectName, apiResponse) {
        // Get the project ID from URL
        const urlParams = new URLSearchParams(window.location.search);
        const pid = urlParams.get('id');

        // Start with the project header
        this.sideBarData = [
            {
                type: "project",
                content: projectName || "Project Name",
                project_id: pid
            }
        ];

        // Add topics from the API response
        if (apiResponse && apiResponse.data && Array.isArray(apiResponse.data)) {
            apiResponse.data.forEach((topic, index) => {
                this.sideBarData.push({
                    type: "topic",
                    content: topic.topic_name,
                    topic_id: topic.topic_id, // Store the topic_id
                    isOpen: false, // Default to closed for all topics
                    apis: [] // Initially no APIs, these would be loaded separately
                });
            });
        }

        // Re-render with the new data
        this.render();
    }

    // New method to update topic APIs
    updateTopicApis(topic_id, apiResponse) {
        // Find the topic in sideBarData
        const topicIndex = this.sideBarData.findIndex(item =>
            item.type === "topic" && item.topic_id === topic_id
        );

        if (topicIndex !== -1) {
            // Transform API data to the format expected by the sidebar
            const apis = apiResponse.data.map(api => ({
                protocol: api.api_type || "REST", // Use api_type as protocol
                content: api.api_name,
                endpoint: api.endpoint,
                format: api.format_api,
                api_id: api.api_id
            }));

            // Update the APIs array for this topic
            this.sideBarData[topicIndex].apis = apis;

            // Keep the topic open
            this.sideBarData[topicIndex].isOpen = true;

            // Re-render the sidebar with updated data
            this.render();
        }
    }

    // Updated function to log topic_id when topic is opened
    topicOpen(topic) {
        console.log(`Topic opened: ${topic.topic_id}`);
        // Log additional topic details if needed
        console.log(`Topic details:`, topic);

        // Load APIs for this topic
        loadApiList(topic.topic_id);
    }

    getProtocolClass(protocol) {
        switch (protocol) {
            case 'GET':
                return 'api-get';
            case 'POST':
                return 'api-post';
            case 'PATCH':
                return 'api-patch';
            case 'DELETE':
                return 'api-delete';
            case 'PUT':
                return 'api-put';
            case 'REST':
                return 'api-get';
            case 'GraphQL':
                return 'api-post';
            default:
                return '';
        }
    }

    render() {
        this.sidebarNav.innerHTML = '';

        // Check if we have data to render
        if (this.sideBarData.length === 0) return;

        // Project header with ellipsis menu
        const projectItem = document.createElement('div');
        projectItem.className = 'mb-4 font-semibold pl-2 flex justify-between items-center group';

        const projectText = document.createElement('div');
        projectText.className = 'overflow-hidden whitespace-nowrap';
        projectText.textContent = truncateText(this.sideBarData[0].content, 16);
        projectItem.appendChild(projectText);

        const projectMenu = document.createElement('div');
        projectMenu.className = 'opacity-0 group-hover:opacity-100 transition-opacity duration-200 cursor-pointer px-2';
        projectMenu.innerHTML = '<i class="fa-solid fa-ellipsis text-xs"></i>';

        // Add event listener for project menu
        projectMenu.addEventListener('click', (e) => {
            const projectId = this.sideBarData[0].project_id;
            const projectName = this.sideBarData[0].content;

            showContextMenu(e, [
                {
                    label: 'Add Topic',
                    icon: 'fa-solid fa-plus',
                    action: () => renameProject(projectId, projectName)
                },
                {
                    label: 'Rename Project',
                    icon: 'fa-solid fa-pen',
                    action: () => renameProject(projectId, projectName)
                },
                {
                    label: 'Delete Project',
                    icon: 'fa-solid fa-trash text-red-500',
                    action: () => deleteProject(projectId)
                }
            ]);
        });

        projectItem.appendChild(projectMenu);
        this.sidebarNav.appendChild(projectItem);

        // Topics container
        const topicsContainer = document.createElement('div');
        topicsContainer.className = 'space-y-2';
        this.sidebarNav.appendChild(topicsContainer);

        // Render topics
        this.sideBarData.slice(1).forEach((topic) => {
            const topicElement = this.createTopicElement(topic);
            topicsContainer.appendChild(topicElement);
        });
    }

    createTopicElement(topic) {
        const topicContainer = document.createElement('div');
        topicContainer.className = 'mb-1';

        // Topic header
        const topicHeader = document.createElement('div');
        const isActive = topic.isOpen;
        topicHeader.className = `flex justify-between items-center group p-1 menu-item-hover transition-all duration-200 ${isActive ? 'topic-active' : ''}`;

        topicHeader.innerHTML = `
            <div class="flex items-center">
                <i class="fa-${topic.isOpen ? 'solid fa-folder-open folder-open-icon' : 'regular fa-folder folder-icon'} text-sm"></i>
                <div class="ml-2 text-sm overflow-hidden whitespace-nowrap max-w-[130px] topic-text ${isActive ? 'font-medium' : ''}">${truncateText(topic.content, 16)}</div>
            </div>
            <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <i class="fa-solid fa-ellipsis text-xs"></i>
            </div>
        `;

        // Toggle topic open/closed
        topicHeader.addEventListener('click', () => {
            topic.isOpen = !topic.isOpen;

            // Call topicOpen when topic is opened
            if (topic.isOpen) {
                this.topicOpen(topic);
            }

            this.render();
        });

        topicContainer.appendChild(topicHeader);

        // API list (if topic is open)
        if (topic.isOpen && topic.apis && topic.apis.length > 0) {
            const apisContainer = document.createElement('div');
            apisContainer.className = 'ml-4 mt-1 space-y-1 pl-2 border-l border-opacity-50';

            topic.apis.forEach(api => {
                const apiItem = this.createApiElement(api);
                apisContainer.appendChild(apiItem);
            });

            topicContainer.appendChild(apisContainer);
        }

        return topicContainer;
    }

    createApiElement(api) {
        const apiItem = document.createElement('div');
        apiItem.className = 'flex justify-between items-center group px-2 py-1 menu-item-hover transition-all duration-200 cursor-pointer';

        const protocolClass = this.getProtocolClass(api.protocol);

        apiItem.innerHTML = `
            <div class="flex items-center">
                <div class="mr-2 font-medium text-xs ${protocolClass}">${api.protocol}</div>
                <div class="text-sm overflow-hidden whitespace-nowrap max-w-[100px]">${truncateText(api.content, 12 - api.protocol.length)}</div>
            </div>
            <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <i class="fa-solid fa-ellipsis text-xs"></i>
            </div>
        `;

        // Handle API click event
        apiItem.addEventListener('click', () => {
            console.log(`API clicked: ${api.protocol} ${api.content}`);
            console.log(`Endpoint: ${api.endpoint}`);

            // Load API details into the main content area instead of navigating
            loadApiContent(api);
        });

        return apiItem;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Sidebar();
});

export default Sidebar;