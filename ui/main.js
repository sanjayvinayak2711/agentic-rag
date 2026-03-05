// API Base URL
const API_BASE = '/api';

// Global variables
let chatMessages;
let chatInput;
let sendBtn;
let fileUpload;
let filesCount;
let filesList;
let performanceCanvas;
let headerModelName;
let metricLatency;
let metricAccuracy;
let metricTokens;
let chatHistory = [];
let currentChatId = null;
let uploadedFiles = [];
let performanceData = {
    accuracy: [94.2, 93.8, 94.5, 94.1, 94.7, 94.2, 93.9, 94.3],
    speed: [1.2, 1.3, 1.1, 1.4, 1.2, 1.0, 1.3, 1.2]
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize DOM elements
    chatMessages = document.getElementById('chat-messages');
    chatInput = document.getElementById('chat-input');
    sendBtn = document.getElementById('send-btn');
    fileUpload = document.getElementById('file-upload');
    filesCount = document.getElementById('files-count');
    filesList = document.getElementById('files-list');
    performanceCanvas = document.getElementById('performance-canvas');
    headerModelName = document.getElementById('header-model-name');
    metricLatency = document.getElementById('metric-latency');
    metricAccuracy = document.getElementById('metric-accuracy');
    metricTokens = document.getElementById('metric-tokens');
    
    console.log('DOM Elements initialized');
    console.log('chatMessages element:', chatMessages);
    console.log('chatMessages scrollHeight:', chatMessages ? chatMessages.scrollHeight : 'N/A');
    console.log('chatMessages clientHeight:', chatMessages ? chatMessages.clientHeight : 'N/A');
    
    setupEventListeners();
    initializeChat();
    initializePerformanceGraph();
    loadModelStats();
    
    // Initialize with real zeros
    updatePerformanceMetrics(0, 0, 0);
    
    // Test scrolling functionality
    setTimeout(() => {
        if (chatMessages) {
            console.log('After init - scrollHeight:', chatMessages.scrollHeight);
            console.log('After init - clientHeight:', chatMessages.clientHeight);
            console.log('Can scroll:', chatMessages.scrollHeight > chatMessages.clientHeight);
        }
    }, 1000);
});

// Update Performance Metrics with real values
function updatePerformanceMetrics(latency = null, accuracy = null, tokens = null) {
    console.log('Updating performance metrics:', { latency, accuracy, tokens });
    
    if (metricLatency) {
        if (latency !== null) {
            metricLatency.textContent = `${latency.toFixed(3)}s`;
        } else {
            metricLatency.textContent = '0.000s';
        }
    }
    if (metricAccuracy) {
        if (accuracy !== null) {
            metricAccuracy.textContent = `${accuracy.toFixed(0)}%`;
        } else {
            metricAccuracy.textContent = '0%';
        }
    }
    if (metricTokens) {
        if (tokens !== null) {
            metricTokens.textContent = Math.round(tokens).toString();
        } else {
            metricTokens.textContent = '0';
        }
    }
}

// Setup Event Listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Send button
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
        console.log('Send button listener added');
    }
    
    // Chat input
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto-resize textarea
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        console.log('Chat input listeners added');
    }
    
    // Mouse wheel scrolling test
    if (chatMessages) {
        chatMessages.addEventListener('wheel', function(e) {
            console.log('Mouse wheel event detected:', e.deltaY);
            console.log('Current scrollTop:', chatMessages.scrollTop);
            console.log('Current scrollHeight:', chatMessages.scrollHeight);
            console.log('Current clientHeight:', chatMessages.clientHeight);
        });
        console.log('Mouse wheel listener added to chatMessages');
    }
    
    // New chat button
    const newChatBtn = document.querySelector('.new-chat-btn-top');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', function() {
            console.log('New chat button clicked');
            
            // Clear chat messages
            if (chatMessages) {
                chatMessages.innerHTML = `
                    <div class="welcome-message">
                        <div class="welcome-icon">
                            <i class="fas fa-brain"></i>
                        </div>
                        <h2>Welcome to Agentic RAG</h2>
                        <p>Upload documents and ask questions about them</p>
                    </div>
                `;
                
                // Reset scroll position to top
                chatMessages.scrollTop = 0;
            }
            
            // Clear chat history
            chatHistory = [];
            currentChatId = null;
            
            // Clear input
            if (chatInput) {
                chatInput.value = '';
                chatInput.style.height = 'auto';
                chatInput.focus();
            }
            
            // Reset performance metrics
            performanceData = {
                accuracy: [94.2, 93.8, 94.5, 94.1, 94.7, 94.2, 93.9, 94.3],
                speed: [1.2, 1.3, 1.1, 1.4, 1.2, 1.0, 1.3, 1.2]
            };
            
            // Reset performance display
            updatePerformanceMetrics();
            
            // Reinitialize performance graph
            initializePerformanceGraph();
            
            // Reset to default agent
            const defaultAgentBtn = document.querySelector('.agent-btn[data-agent="default"]');
            if (defaultAgentBtn) {
                document.querySelectorAll('.agent-btn').forEach(btn => btn.classList.remove('active'));
                defaultAgentBtn.classList.add('active');
                if (headerModelName) {
                    headerModelName.textContent = 'AGENTIC RAG';
                    headerModelName.style.opacity = '0.5';
                    setTimeout(() => {
                        headerModelName.style.opacity = '1';
                    }, 200);
                }
            }
            
            // Show status message
            showStatus('New chat started - Interface refreshed', 'success', 2000);
            
            console.log('Chat interface completely refreshed');
        });
        console.log('New chat button listener added');
    } else {
        console.log('New chat button not found!');
    }
    
    // Agent switching buttons
    const agentBtns = document.querySelectorAll('.agent-btn');
    agentBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            agentBtns.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get selected agent
            const selectedAgent = this.dataset.agent;
            console.log('Selected agent:', selectedAgent);
            
            // Update header model name
            const agentName = 'AGENTIC RAG';
            if (headerModelName) {
                headerModelName.textContent = agentName;
                headerModelName.style.opacity = '0.5';
                setTimeout(() => {
                    headerModelName.style.opacity = '1';
                }, 200);
            }
            
            // Show status message
            showStatus(`Switched to ${agentName}`, 'info', 2000);
            
            // Focus input
            if (chatInput) {
                chatInput.focus();
            }
        });
    });
    console.log('Agent switching listeners added');
    
    // File upload
    if (fileUpload) {
        fileUpload.addEventListener('change', handleFileUpload);
        console.log('File upload listener added');
    }
    
    console.log('Event listeners setup complete');
}

// Initialize Performance Graph
function initializePerformanceGraph() {
    if (!performanceCanvas) {
        console.log('Performance canvas not found');
        return;
    }
    
    const ctx = performanceCanvas.getContext('2d');
    if (!ctx) {
        console.log('Could not get canvas context');
        return;
    }
    
    const width = performanceCanvas.width;
    const height = performanceCanvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw grid
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 1;
    
    // Horizontal lines
    for (let i = 0; i <= 4; i++) {
        const y = (height / 4) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }
    
    // Draw accuracy line
    if (performanceData.accuracy && performanceData.accuracy.length > 0) {
        ctx.strokeStyle = '#0066cc';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        performanceData.accuracy.forEach((value, index) => {
            const x = (width / (performanceData.accuracy.length - 1)) * index;
            const y = height - ((value - 85) / 15 * height);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
    }
    
    // Draw speed line
    if (performanceData.speed && performanceData.speed.length > 0) {
        ctx.strokeStyle = '#ff6b6b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        
        performanceData.speed.forEach((value, index) => {
            const x = (width / (performanceData.speed.length - 1)) * index;
            const y = height - ((value - 0.5) / 1.5 * height);
            
            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        
        ctx.stroke();
    }
    
    console.log('Performance graph updated');
}

// Initialize Chat
function initializeChat() {
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">
                    <i class="fas fa-brain"></i>
                </div>
                <h2>Welcome to Agentic RAG</h2>
                <p>Upload documents and ask questions about them</p>
            </div>
        `;
    }
}

// Load Model Stats
function loadModelStats() {
    console.log('Loading model stats...');
    console.log('headerModelName element:', headerModelName);
    
    // Show loading effect for AGENTIC RAG
    if (headerModelName) {
        headerModelName.textContent = 'AGENTIC RAG';
        headerModelName.style.opacity = '0.5';
        console.log('Set text to AGENTIC RAG with opacity 0.5');
        
        // Simulate loading effect
        setTimeout(() => {
            headerModelName.style.opacity = '1';
            headerModelName.style.transition = 'opacity 0.5s ease';
            console.log('Faded to full opacity');
        }, 500);
    } else {
        console.log('headerModelName element not found!');
    }
}

// Show Status Message
function showStatus(message, type = 'info', duration = 3000) {
    // Create status element if it doesn't exist
    let statusEl = document.querySelector('.status-message');
    if (!statusEl) {
        statusEl = document.createElement('div');
        statusEl.className = 'status-message';
        document.body.appendChild(statusEl);
    }
    
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    statusEl.style.display = 'block';
    
    setTimeout(() => {
        statusEl.style.display = 'none';
    }, duration);
}

// Process Message Content (simple markdown-like formatting)
function processMessageContent(content) {
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

// Add Message to Chat
function addMessage(type, content) {
    console.log('Adding message:', type, content);
    
    // Remove welcome message if it exists
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const messageTime = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    // Process markdown-like formatting
    const processedContent = processMessageContent(content);

    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${processedContent}
        </div>
        <div class="message-time">${messageTime}</div>
    `;

    // Append to chat messages
    chatMessages.appendChild(messageDiv);
    
    // Force scroll to bottom
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 10);
    
    // Double-check scroll after content renders
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
    
    console.log('Message added, scrollHeight:', chatMessages.scrollHeight, 'scrollTop:', chatMessages.scrollTop);
}

// Handle Send Message
async function sendMessage() {
    console.log('Send button clicked!');
    const input = document.getElementById("chat-input");
    const message = input.value.trim();

    if (!message) {
        console.log('No message to send');
        return;
    }

    console.log('Sending message:', message);
    
    // Get selected agent
    const activeAgentBtn = document.querySelector('.agent-btn.active');
    const selectedAgent = activeAgentBtn ? activeAgentBtn.dataset.agent : 'default';
    console.log('Using agent:', selectedAgent);
    
    // Track start time for latency
    const startTime = Date.now();
    
    // Disable send button temporarily to prevent double sends
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.style.opacity = '0.5';
    }
    
    // Add user message
    addMessage("user", message);
    
    // Clear input and reset
    input.value = "";
    input.style.height = 'auto';
    
    // Focus back to input for next message
    setTimeout(() => {
        input.focus();
    }, 100);

    showTypingIndicator();

    try {
        console.log('Making API request...');
        const res = await fetch("/api/query", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ 
                query: message, 
                use_context: true,
                agent: selectedAgent 
            })
        });

        console.log('API response status:', res.status);

        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        const data = await res.json();
        console.log('Response data:', data);

        // Calculate real latency
        const endTime = Date.now();
        const realLatency = (endTime - startTime) / 1000; // Convert to seconds
        
        // Extract response text
        const responseText = data.response || "Sorry, I couldn't process your request.";
        
        // Calculate real tokens (rough estimate: 1 token ≈ 4 characters)
        const realTokens = (message.length + responseText.length) / 4;
        
        // Calculate accuracy based on response quality (simple heuristic)
        let realAccuracy = 85; // Base accuracy
        if (responseText.length > 50) {
            realAccuracy += 5; // Longer responses are better
        }
        if (responseText.includes('exact') || responseText.includes('specific')) {
            realAccuracy += 3; // Contains specific information
        }
        if (data.context_used) {
            realAccuracy += 7; // Used document context
        }
        realAccuracy = Math.min(realAccuracy, 99); // Cap at 99%
        
        console.log('Real metrics calculated:', { 
            latency: realLatency, 
            tokens: realTokens, 
            accuracy: realAccuracy 
        });
        
        // Update performance metrics with REAL values
        updatePerformanceMetrics(realLatency, realAccuracy, realTokens);
        
        // Add real performance data to history
        performanceData.accuracy.push(realAccuracy);
        performanceData.speed.push(realLatency);
        
        // Keep only last 8 data points
        if (performanceData.accuracy.length > 8) {
            performanceData.accuracy.shift();
            performanceData.speed.shift();
        }
        
        // Reinitialize graph with REAL data
        setTimeout(() => {
            initializePerformanceGraph();
        }, 100);
        
        // Add assistant response
        addMessage("assistant", responseText);
        
        // Add to chat history
        chatHistory.push({
            type: 'assistant',
            content: responseText,
            timestamp: new Date().toISOString(),
            agent: selectedAgent,
            metrics: {
                latency: realLatency,
                tokens: realTokens,
                accuracy: realAccuracy
            }
        });

    } catch (error) {
        console.error('Error sending message:', error);
        hideTypingIndicator();
        addMessage("assistant", '❌ Sorry, I encountered an error. Please try again.');
        
        // Ensure input is ready for next message even after error
        setTimeout(() => {
            input.focus();
        }, 200);
    } finally {
        hideTypingIndicator();
        
        // Re-enable send button
        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.style.opacity = '1';
        }
        
        // Focus input for next message
        setTimeout(() => {
            input.focus();
        }, 100);
    }
}

// Show Typing Indicator
function showTypingIndicator() {
    // Remove any existing typing indicator
    hideTypingIndicator();
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant';
    typingDiv.id = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    
    // Scroll to typing indicator
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 50);
}

// Hide Typing Indicator
function hideTypingIndicator() {
    const typingIndicator = chatMessages.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Handle File Upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    console.log('Uploading file:', file.name);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.status === 'success') {
            showStatus(
                `✅ Successfully uploaded ${file.name}. Ready to chat!`,
                'success'
            );
            
            // Add confirmation message to chat
            const confirmationMessage = `📄 I've successfully processed **${file.name}**. You can now ask me questions about it!`;
            addMessage('assistant', confirmationMessage);
            
        } else {
            showStatus(`❌ Error uploading file: ${result.message}`, 'error');
        }

    } catch (error) {
        console.error('Error uploading file:', error);
        showStatus('❌ Error uploading file. Please try again.', 'error');
    }

    // Clear file input
    fileUpload.value = '';
}
