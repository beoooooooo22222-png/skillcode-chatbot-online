// Function to add message to chat
function addMessage(sender, text) {
    const container = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatText(text);

    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;

    return messageDiv;
}

// Function to add a PDF download button to a message
function addDownloadButton(messageDiv, filename) {
    if (!messageDiv) return;

    // Find content div
    const contentDiv = messageDiv.querySelector('.message-content');
    if (!contentDiv) return;

    // Create actions container if it doesn't exist
    let actionsDiv = messageDiv.querySelector('.message-actions');
    if (!actionsDiv) {
        actionsDiv = document.createElement('div');
        actionsDiv.className = 'message-actions';
        actionsDiv.style.marginTop = '8px';
        actionsDiv.style.display = 'flex';
        actionsDiv.style.justifyContent = 'flex-end';
        messageDiv.appendChild(actionsDiv);
    }

    // Create Download PDF button
    const pdfBtn = document.createElement('button');
    pdfBtn.innerHTML = '📄 Download PDF';
    pdfBtn.className = 'download-pdf-btn';

    // Style the button
    Object.assign(pdfBtn.style, {
        padding: '6px 12px',
        fontSize: '12px',
        cursor: 'pointer',
        backgroundColor: '#fff',
        border: '1px solid #e2e8f0',
        borderRadius: '6px',
        color: '#475569',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        transition: 'all 0.2s'
    });

    // Hover effect
    pdfBtn.onmouseover = () => {
        pdfBtn.style.backgroundColor = '#f8fafc';
        pdfBtn.style.borderColor = '#cbd5e1';
    };
    pdfBtn.onmouseout = () => {
        pdfBtn.style.backgroundColor = '#fff';
        pdfBtn.style.borderColor = '#e2e8f0';
    };

    pdfBtn.addEventListener('click', async () => {
        if (typeof html2pdf === 'undefined') {
            alert('PDF library is loading or failed to load. Please try again.');
            return;
        }

        // Show processing state
        const originalText = pdfBtn.innerHTML;
        pdfBtn.innerHTML = '⏳ Processing...';
        pdfBtn.disabled = true;

        // Create a professional PDF container
        const pdfWrapper = document.createElement('div');
        pdfWrapper.style.padding = '40px';
        pdfWrapper.style.backgroundColor = 'white';
        pdfWrapper.style.color = '#1a202c';
        pdfWrapper.style.fontFamily = "'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
        pdfWrapper.style.lineHeight = '1.6';

        // Add Header
        const header = document.createElement('div');
        header.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 20px;">
                <div style="font-size: 24px; font-weight: bold; color: #667eea;">SkillCode GPT</div>
                <div style="font-size: 12px; color: #718096;">Generated on ${new Date().toLocaleDateString()}</div>
            </div>
            <div style="font-size: 18px; font-weight: 600; margin-bottom: 20px; color: #2d3748;">
                Topic: ${filename.replace(/_/g, ' ')}
            </div>
        `;
        pdfWrapper.appendChild(header);

        // Clone the content
        const clonedContent = contentDiv.cloneNode(true);

        // Fix for Mermaid diagrams: ensure SVGs are visible and text is black
        clonedContent.querySelectorAll('.mermaid').forEach(m => {
            m.style.backgroundColor = '#f8fafc';
            m.style.border = '1px solid #e2e8f0';
            m.style.padding = '20px';
            m.style.borderRadius = '8px';
            m.style.textAlign = 'center';
            m.style.marginBottom = '20px';
            // Scale Mermaid if too large
            m.style.overflow = 'visible';
        });

        // Improve text readability in PDF
        clonedContent.querySelectorAll('strong, b').forEach(s => s.style.color = '#2d3748');
        clonedContent.style.fontSize = '14px';

        pdfWrapper.appendChild(clonedContent);

        // Prepare diagrams for capture BEFORE generating PDF
        await prepareMermaidForExport(pdfWrapper);

        // Add Footer
        const footer = document.createElement('div');
        footer.innerHTML = `
            <div style="margin-top: 30px; padding-top: 10px; border-top: 1px solid #e2e8f0; font-size: 10px; color: #a0aec0; text-align: center;">
                Powered by SkillCode GPT Educational Assistant. All rights reserved.
            </div>
        `;
        pdfWrapper.appendChild(footer);

        const opt = {
            margin: [10, 10, 10, 10],
            filename: `${filename}_${new Date().toISOString().slice(0, 10)}.pdf`,
            image: { type: 'jpeg', quality: 1.0 },
            html2canvas: {
                scale: 3, // Higher scale for extreme clarity
                useCORS: true,
                logging: false,
                letterRendering: true,
                onclone: (doc) => {
                    // Final tweaks inside the canvas capture if needed
                }
            },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
        };

        html2pdf().set(opt).from(pdfWrapper).save().then(() => {
            pdfBtn.innerHTML = originalText;
            pdfBtn.disabled = false;
        }).catch(err => {
            console.error('PDF Generation Error:', err);
            pdfBtn.innerHTML = '❌ Error';
            setTimeout(() => {
                pdfBtn.innerHTML = originalText;
                pdfBtn.disabled = false;
            }, 3000);
        });
    });

    actionsDiv.appendChild(pdfBtn);
}

// Function to load a specific conversation into the chat
function loadConversationIntoChat(userMessage, aiResponse) {
    const container = document.getElementById('messagesContainer');
    if (!container) return;

    // Add a separator to show this is a loaded conversation
    const separator = document.createElement('div');
    separator.className = 'history-separator';
    separator.innerHTML = '<span>── Loaded from History ──</span>';
    container.appendChild(separator);

    // Add the user message
    addMessage('user', userMessage);

    // Add the AI response
    const botMessageDiv = addMessage('bot', aiResponse);

    // Add Download Button for relevant assistants
    if (typeof assistantType !== 'undefined' && ['mind_map', 'exam', 'study_plan'].includes(assistantType)) {
        addDownloadButton(botMessageDiv, assistantType);
    }

    // Scroll to the loaded conversation
    container.scrollTop = container.scrollHeight;

    // Trigger diagram rendering if needed
    renderDiagrams();
}

// Format text with line breaks and basic markdown
function formatText(text) {
    // Check for Mermaid blocks (handle variations like ```mermaid or ``` mermaid)
    const mermaidRegex = /```\s*mermaid([\s\S]*?)```/g;
    let match;
    let lastIndex = 0;
    let formatted = '';

    while ((match = mermaidRegex.exec(text)) !== null) {
        // Add text before the mermaid block
        formatted += text.substring(lastIndex, match.index).replace(/\n/g, '<br>');

        // Add the mermaid block with basic sanitization
        let mermaidCode = match[1].trim();

        // Basic cleanup for Mermaid: ensure no trailing empty lines that cause errors
        mermaidCode = mermaidCode.split('\n').map(line => line.trim()).filter(line => line).join('\n');

        formatted += `<div class="mermaid">${mermaidCode}</div>`;

        lastIndex = mermaidRegex.lastIndex;
    }

    // Add remaining text
    formatted += text.substring(lastIndex).replace(/\n/g, '<br>');

    // Apply basic markdown
    return formatted
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

// Function to trigger Mermaid rendering if library is present
function renderDiagrams() {
    if (typeof mermaid !== 'undefined') {
        try {
            mermaid.run();
        } catch (e) {
            console.error('Mermaid render error:', e);
            // Optionally show error in the UI
            document.querySelectorAll('.mermaid').forEach(el => {
                if (el.getAttribute('data-processed') === 'error') {
                    el.innerHTML = '<div style="color:red; padding:10px; border:1px solid red; border-radius:8px;">⚠️ Syntax Error in Mind Map. Try asking again.</div>';
                }
            });
        }
    }
}

/**
 * Helper to convert Mermaid SVGs to static images for PDF export
 * Resolves the issue where SVGs are missing in PDF downloads
 */
async function prepareMermaidForExport(element) {
    const mermaidDivs = element.querySelectorAll('.mermaid');
    if (mermaidDivs.length === 0) return;

    // Temporarily append to body to ensure getBBox() and clientWidth work
    // Position it off-screen so it's not visible to the user
    element.style.position = 'fixed';
    element.style.top = '-9999px';
    element.style.left = '-9999px';
    element.style.width = '800px'; // Standard A4 width approx
    document.body.appendChild(element);

    // Extract all Mermaid-related styles from the document
    let mermaidStyles = '';
    const styleSheets = document.styleSheets;
    for (let i = 0; i < styleSheets.length; i++) {
        try {
            const rules = styleSheets[i].cssRules || styleSheets[i].rules;
            for (let j = 0; j < rules.length; j++) {
                if (rules[j].selectorText && (rules[j].selectorText.includes('mermaid') || rules[j].selectorText.includes('.node'))) {
                    mermaidStyles += rules[j].cssText;
                }
            }
        } catch (e) {
            // Skip cross-origin stylesheets
        }
    }

    const promises = Array.from(mermaidDivs).map(async (div) => {
        const svg = div.querySelector('svg');
        if (!svg) return;

        // Set explicit dimensions - essential for invisible elements
        const rect = svg.getBoundingClientRect();
        const width = rect.width || 800; // Fallback
        const height = rect.height || 600;

        // Clone SVG and inject styles
        const clonedSvg = svg.cloneNode(true);
        const styleElement = document.createElementNS("http://www.w3.org/2000/svg", "style");
        styleElement.textContent = mermaidStyles;
        clonedSvg.insertBefore(styleElement, clonedSvg.firstChild);

        // Serialize SVG to XML
        const serializer = new XMLSerializer();
        let svgXml = serializer.serializeToString(clonedSvg);

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        const scale = 2; // High enough for clarity
        canvas.width = width * scale;
        canvas.height = height * scale;
        ctx.scale(scale, scale);
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const img = new Image();
        const svgBlob = new Blob([svgXml], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(svgBlob);

        return new Promise((resolve) => {
            img.onload = () => {
                ctx.drawImage(img, 0, 0, width, height);
                const dataUrl = canvas.toDataURL('image/png');
                const staticImg = document.createElement('img');
                staticImg.src = dataUrl;
                staticImg.style.width = '100%';
                staticImg.style.display = 'block';
                staticImg.className = 'mermaid-static-image';

                svg.classList.add('pdf-hidden');
                svg.style.display = 'none';
                div.appendChild(staticImg);

                URL.revokeObjectURL(url);
                resolve();
            };
            img.onerror = (err) => {
                console.error("SVG Capture Error:", err);
                resolve();
            };
            img.src = url;
        });
    });

    await Promise.all(promises);

    // Remove temporary export element from DOM
    document.body.removeChild(element);

    // Reset styles for regular usage
    element.style.position = '';
    element.style.top = '';
    element.style.left = '';
    element.style.width = '';
}

// Show loading indicator
function showLoading() {
    const container = document.getElementById('messagesContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.id = 'loading-message';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content loading';
    contentDiv.innerHTML = '<div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div>';

    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

// Remove loading indicator
function removeLoading() {
    const loadingMsg = document.getElementById('loading-message');
    if (loadingMsg) {
        loadingMsg.remove();
    }
}

// Send message function
function sendMessage(event, assistantType, customParams = {}) {
    event.preventDefault();

    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    addMessage('user', message);
    input.value = '';

    // Show loading
    showLoading();

    // Prepare request
    const requestData = {
        message: message,
        assistant_type: assistantType,
        params: customParams
    };

    // Send to API
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            removeLoading();

            if (data.success) {
                const botMessageDiv = addMessage('bot', data.response);

                // Show sources if available
                if (data.sources && data.sources.length > 0) {
                    const sourcesText = '\n📚 **Reference Materials analyzed:** ' + data.sources.join(', ');
                    addMessage('bot', sourcesText);
                }

                // Trigger visual rendering for mind maps/diagrams
                renderDiagrams();

                // Add Download Button for relevant assistants
                if (['mind_map', 'exam', 'study_plan'].includes(assistantType)) {
                    addDownloadButton(botMessageDiv, assistantType);
                }

                // Refresh history sidebar
                if (typeof assistantType !== 'undefined') {
                    loadHistory(assistantType, true); // true means refresh sidebar only
                }
            } else {
                addMessage('bot', '❌ Error: ' + (data.error || 'Unknown error occurred'));
            }
        })
        .catch(error => {
            removeLoading();
            console.error('Error:', error);
            addMessage('bot', '❌ Error: Failed to get response. Please try again.');
        });

    // Focus input
    input.focus();
}

// Function to load conversation history
function loadHistory(assistantType, refreshOnly = false) {
    const container = document.getElementById('messagesContainer');
    const historyList = document.getElementById('sidebarHistoryList');

    console.log(`Loading history for ${assistantType} (refreshOnly: ${refreshOnly})`);

    fetch(`/api/conversation-history?type=${assistantType}&limit=500`)
        .then(response => response.json())
        .then(data => {
            console.log('History data received:', data);
            if (data.success && data.conversations.length > 0) {
                // Restore chat bubbles (chronological)
                if (!refreshOnly && container) {
                    const chats = [...data.conversations].reverse();
                    chats.forEach(conv => {
                        addMessage('user', conv.user_message);
                        const botMessageDiv = addMessage('bot', conv.ai_response);

                        // Add Download Button for relevant assistants in initial history load
                        if (['mind_map', 'exam', 'study_plan'].includes(assistantType)) {
                            addDownloadButton(botMessageDiv, assistantType);
                        }
                    });
                    container.scrollTop = container.scrollHeight;
                }

                // Populate Sidebar History
                if (historyList) {
                    historyList.innerHTML = '';
                    data.conversations.forEach(conv => {
                        const item = document.createElement('div');
                        item.className = 'history-item';

                        const snippet = conv.user_message.length > 60
                            ? conv.user_message.substring(0, 60) + '...'
                            : conv.user_message;

                        item.innerHTML = `
                            <div class="history-item-text">${snippet}</div>
                            <div class="history-item-date">${conv.created_at || 'Recent'}</div>
                        `;

                        // Click handler to load this conversation into chat
                        item.addEventListener('click', () => {
                            loadConversationIntoChat(conv.user_message, conv.ai_response);
                        });

                        historyList.appendChild(item);
                    });
                }
            }
        })
        .catch(error => console.error('Error loading history:', error));
}

// Sidebar Toggle Function
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed'));
        updateSidebarToggleIcon();
    }
}

// Function to update the sidebar toggle icon
function updateSidebarToggleIcon() {
    const sidebar = document.querySelector('.sidebar');
    const toggleIcon = document.getElementById('toggleIcon');
    if (sidebar && toggleIcon) {
        toggleIcon.textContent = sidebar.classList.contains('collapsed') ? '▶' : '◀';
    }
}

// Function to load and populate subject dropdowns from available books
async function loadSubjects() {
    const dropdowns = document.querySelectorAll('.subject-dropdown');
    if (dropdowns.length === 0) return;

    console.log('Fetching available books for dropdowns...');
    try {
        const response = await fetch('/api/get-books');
        const data = await response.json();

        if (data.success) {
            const books = data.books;

            // Extract unique subjects and levels from titles
            const subjectsSet = new Set();
            const levelsSet = new Set();

            books.forEach(book => {
                const title = book.title.toLowerCase();

                // Subject extraction
                if (title.includes('arabic') || title.includes('عربي')) subjectsSet.add('Arabic (عربي)');
                else if (title.includes('math') || title.includes('رياضيات')) subjectsSet.add('Mathematics (رياضيات)');
                else if (title.includes('science') || title.includes('علوم')) subjectsSet.add('Science (علوم)');
                else if (title.includes('english')) subjectsSet.add('English');
                else if (title.includes('social') || title.includes('دراسات') || title.includes('history') || title.includes('geography')) subjectsSet.add('Social Studies (دراسات)');
                else if (title.includes('islamic') || title.includes('دين')) subjectsSet.add('Islamic (دين)');

                // Level extraction
                if (title.includes('prim1')) levelsSet.add('Primary 1');
                if (title.includes('prim2')) levelsSet.add('Primary 2');
                if (title.includes('prim3')) levelsSet.add('Primary 3');
                if (title.includes('prim4')) levelsSet.add('Primary 4');
                if (title.includes('prim5')) levelsSet.add('Primary 5');
                if (title.includes('prim6')) levelsSet.add('Primary 6');
                if (title.includes('prep1')) levelsSet.add('Preparatory 1');
                if (title.includes('prep2')) levelsSet.add('Preparatory 2');
                if (title.includes('prep3')) levelsSet.add('Preparatory 3');
            });

            const subjects = Array.from(subjectsSet).sort();
            const levels = Array.from(levelsSet).sort();

            dropdowns.forEach(dropdown => {
                const currentValue = dropdown.value;
                dropdown.innerHTML = '<option value="">All Subjects / Books</option>';

                // Section 1: Broad Subjects
                const optGroupSubjects = document.createElement('optgroup');
                optGroupSubjects.label = 'Education Subjects';
                subjects.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s;
                    opt.textContent = s;
                    optGroupSubjects.appendChild(opt);
                });
                dropdown.appendChild(optGroupSubjects);

                // Section 2: Education Levels
                const optGroupLevels = document.createElement('optgroup');
                optGroupLevels.label = 'Specific Grade Levels';
                levels.forEach(l => {
                    const opt = document.createElement('option');
                    opt.value = l;
                    opt.textContent = l;
                    optGroupLevels.appendChild(opt);
                });
                dropdown.appendChild(optGroupLevels);

                // Section 3: Exact Books
                const optGroupBooks = document.createElement('optgroup');
                optGroupBooks.label = 'Specific Curriculum Books';
                books.forEach(book => {
                    const opt = document.createElement('option');
                    opt.value = book.title;
                    opt.textContent = book.title;
                    optGroupBooks.appendChild(opt);
                });
                dropdown.appendChild(optGroupBooks);

                // Restore value if it still exists
                if (currentValue) dropdown.value = currentValue;
            });
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
    }
}

// Function to toggle customization panels
function togglePanel(event) {
    const panel = event.currentTarget.closest('.customization-panel');
    if (panel) {
        panel.classList.toggle('collapsed');

        // Save state in localStorage
        const panelId = panel.id || 'default-panel';
        localStorage.setItem(`panel_${panelId}_collapsed`, panel.classList.contains('collapsed'));
    }
}

// Store initial welcome message
let initialWelcomeMessage = '';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('messagesContainer');
    if (container) {
        initialWelcomeMessage = container.innerHTML;
    }

    const input = document.getElementById('messageInput');
    if (input) {
        input.focus();
    }

    // Load available books for dropdowns
    loadSubjects();

    // Attach collapsible panel listeners
    const panelHeaders = document.querySelectorAll('.panel-header');
    panelHeaders.forEach(header => {
        header.addEventListener('click', togglePanel);

        const panel = header.closest('.customization-panel');
        const panelId = panel.id || 'default-panel';
        const isCollapsed = localStorage.getItem(`panel_${panelId}_collapsed`) === 'true';
        if (isCollapsed) {
            panel.classList.add('collapsed');
        }
    });

    // Attach Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggleBtn');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Restore Sidebar State
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        const isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
        }
        updateSidebarToggleIcon();
    }

    // Load history if assistantType is defined
    if (typeof assistantType !== 'undefined') {
        loadHistory(assistantType);
    }
});

// Allow Enter to send message (Shift+Enter for new line)
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('messageInput');
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const form = input.closest('form');
                form.dispatchEvent(new Event('submit'));
            }
        });
    }
});

function startNewChat() {
    const container = document.getElementById('messagesContainer');
    if (container) {
        container.innerHTML = initialWelcomeMessage;
        const msg = container.querySelector('.message');
        if (msg) {
            msg.style.animation = 'slideIn 0.3s ease-out';
        }
    }
    const input = document.getElementById('messageInput');
    if (input) {
        input.value = '';
        input.focus();
    }
}

function downloadFullChat(assistantName = 'Educational_Chat') {
    const container = document.getElementById('messagesContainer');
    if (!container) return;

    if (typeof html2pdf === 'undefined') {
        alert('PDF library is loading or failed to load. Please try again.');
        return;
    }

    const title = document.querySelector('h1')?.innerText?.replace(/[^a-z0-9]/gi, '_') || assistantName;
    const date = new Date().toISOString().slice(0, 10);
    const filename = `${title}_Full_Chat_${date}.pdf`;

    // Create a special hidden export container to format the PDF nicely
    const pdfWrapper = document.createElement('div');
    pdfWrapper.style.padding = '40px';
    pdfWrapper.style.backgroundColor = 'white';
    pdfWrapper.style.color = '#1a202c';
    pdfWrapper.style.fontFamily = "'Segoe UI', Roboto, sans-serif";

    // Header for full chat
    const header = document.createElement('div');
    header.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #667eea; padding-bottom: 15px; margin-bottom: 30px;">
            <div>
                <div style="font-size: 28px; font-weight: bold; color: #667eea;">SkillCode GPT</div>
                <div style="font-size: 14px; color: #4a5568;">Comprehensive Study Resource</div>
            </div>
            <div style="text-align: right; font-size: 12px; color: #718096;">
                Assistant: ${title.replace(/_/g, ' ')}<br>
                User: ${document.querySelector('.user-info')?.innerText || 'Student'}<br>
                Date: ${new Date().toLocaleDateString()}
            </div>
        </div>
    `;
    pdfWrapper.appendChild(header);

    // Deep clone the messages
    const messages = container.querySelectorAll('.message');
    messages.forEach(msg => {
        const isBot = msg.classList.contains('bot-message');
        const content = msg.querySelector('.message-content');
        if (!content) return;

        const msgDiv = document.createElement('div');
        msgDiv.style.marginBottom = '25px';
        msgDiv.style.padding = '15px';
        msgDiv.style.borderRadius = '8px';
        msgDiv.style.backgroundColor = isBot ? '#f7fafc' : '#ebf4ff';
        msgDiv.style.borderLeft = isBot ? '4px solid #667eea' : '4px solid #4299e1';

        const senderLabel = document.createElement('div');
        senderLabel.style.fontWeight = 'bold';
        senderLabel.style.fontSize = '12px';
        senderLabel.style.marginBottom = '8px';
        senderLabel.style.color = isBot ? '#667eea' : '#4299e1';
        senderLabel.innerText = isBot ? '🤖 SKILLCODE GPT' : '👤 STUDENT';
        msgDiv.appendChild(senderLabel);

        const contentClone = content.cloneNode(true);
        // Remove download buttons and actions from clone
        contentClone.querySelectorAll('button, .message-actions').forEach(b => b.remove());

        // Ensure white background for mermaid icons in full chat
        contentClone.querySelectorAll('.mermaid').forEach(m => {
            m.style.backgroundColor = 'white';
            m.style.border = '1px solid #e2e8f0';
            m.style.padding = '10px';
            m.style.margin = '10px 0';
        });

        msgDiv.appendChild(contentClone);
        pdfWrapper.appendChild(msgDiv);
    });

    // Prepare all diagrams in the full chat wrapper
    prepareMermaidForExport(pdfWrapper).then(() => {
        // Add final footer
        const footer = document.createElement('div');
        footer.innerHTML = `<div style="text-align: center; margin-top: 40px; font-size: 11px; color: #a0aec0;">Page 1 of 1 | Empowering your education journey with AI.</div>`;
        pdfWrapper.appendChild(footer);

        const opt = {
            margin: [10, 10, 15, 10],
            filename: filename,
            image: { type: 'jpeg', quality: 1.0 },
            html2canvas: {
                scale: 2,
                useCORS: true,
                logging: false,
                svgRendering: true
            },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
        };

        html2pdf().set(opt).from(pdfWrapper).save().catch(err => {
            console.error('PDF Full Export Error:', err);
            alert('Failed to generate full PDF.');
        });
    });
}
