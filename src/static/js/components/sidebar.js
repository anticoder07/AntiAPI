/**
 * Sidebar Component
 * Handles the sidebar navigation tree
 */
import { truncateText } from '../utils/helpers.js';

class Sidebar {
    constructor() {
        this.sidebarNav = document.getElementById('sidebar-nav');

        if (!this.sidebarNav) return;

        this.sideBarData = [
            {
                type: "project",
                content: "Project Name"
            },
            {
                type: "topic",
                content: "Topic 1 name",
                isOpen: true,
                apis: [
                    { type: "api", protocol: "GET", content: "API 111111111111111111" },
                    { type: "api", protocol: "POST", content: "API 2" },
                    { type: "api", protocol: "PATCH", content: "API 33333" },
                ]
            },
            {
                type: "topic",
                content: "Topic 2 name",
                isOpen: false,
                apis: []
            },
            {
                type: "topic",
                content: "Topic 3 name",
                isOpen: false,
                apis: []
            },
        ];

        this.render();
    }

    getProtocolClass(protocol) {
        switch (protocol) {
            case 'GET': return 'api-get';
            case 'POST': return 'api-post';
            case 'PATCH': return 'api-patch';
            case 'DELETE': return 'api-delete';
            default: return '';
        }
    }

    render() {
        this.sidebarNav.innerHTML = '';

        // Project header
        const projectItem = document.createElement('div');
        projectItem.className = 'mb-4 font-semibold pl-2';
        projectItem.textContent = truncateText(this.sideBarData[0].content, 16);
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
            // Navigate to API details or perform action
        });

        return apiItem;
    }
}

// Initialize sidebar
document.addEventListener('DOMContentLoaded', () => {
    new Sidebar();
});

export default Sidebar;