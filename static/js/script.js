document.addEventListener('DOMContentLoaded', function() {
    // 全局变量
    let currentStatus = null;
    let apiConfig = {}; // 存储当前API配置（用于主界面设置）
    let saveTimer = null; // 定时器句柄

    // DOM 元素
    const avatarContainer = document.getElementById('avatarContainer');
    const infoPanel = document.getElementById('infoPanel');
    const gfName = document.getElementById('gfName');
    const statusPanel = document.getElementById('statusPanel');
    const chatHistory = document.getElementById('chatHistory');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const renameBtn = document.getElementById('renameBtn');
    const resetBtn = document.getElementById('resetBtn');
    const useApiCheck = document.getElementById('useApi');
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    const settingsForm = document.getElementById('settingsForm');

    // 创建模态框元素
    const createModal = document.getElementById('createModal');
    const createForm = document.getElementById('createForm');
    const testConnectionBtn = document.getElementById('testConnectionBtn');
    const connectionResult = document.getElementById('connectionResult');
    const useApiCreate = document.getElementById('useApiCreate');

    // 初始化：加载常量，填充表单，并尝试获取现有女友状态
    fetch('/api/constants')
        .then(res => res.json())
        .then(data => {
            populateCreateForm(data);
            // 尝试获取当前女友状态
            return fetch('/api/status');
        })
        .then(res => res.json())
        .then(data => {
            if (!data.error) {
                // 已有女友，隐藏创建模态框，显示主界面
                currentStatus = data;
                updateStatus();
                addMessage('系统', `欢迎回来，你正在和 ${currentStatus.name} 交往。`);
                createModal.classList.remove('show');
                startAutoSave(); // 启动自动保存
            } else {
                // 无女友，显示创建模态框
                createModal.classList.add('show');
            }
        })
        .catch(err => {
            console.log('获取状态失败，显示创建模态框');
            createModal.classList.add('show');
        });

    // 启动自动保存（每30秒）
    function startAutoSave() {
        if (saveTimer) clearInterval(saveTimer);
        saveTimer = setInterval(function() {
            fetch('/api/save', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (!data.success) console.log('自动保存失败');
                })
                .catch(err => console.log('自动保存错误', err));
        }, 30000); // 30秒
    }

    // 停止自动保存
    function stopAutoSave() {
        if (saveTimer) {
            clearInterval(saveTimer);
            saveTimer = null;
        }
    }

    // 填充创建表单
    function populateCreateForm(constants) {
        const profSelect = document.getElementById('profession');
        fetch('/api/professions')
            .then(res => res.json())
            .then(profs => {
                profs.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p;
                    opt.textContent = p;
                    profSelect.appendChild(opt);
                });
            });

        const hairSelect = document.getElementById('hairStyle');
        constants.hair_styles.forEach(h => {
            const opt = document.createElement('option');
            opt.value = h;
            opt.textContent = h;
            hairSelect.appendChild(opt);
        });

        const faceSelect = document.getElementById('faceShape');
        constants.face_shapes.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f;
            opt.textContent = f;
            faceSelect.appendChild(opt);
        });

        const personalitySelect = document.getElementById('personality');
        constants.personality_options.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            personalitySelect.appendChild(opt);
        });

        // 设置默认值
        document.getElementById('height').value = Math.floor((constants.height_range[0] + constants.height_range[1])/2);
        document.getElementById('weight').value = 60;
    }

    // 点击头像展开/折叠信息面板
    avatarContainer.addEventListener('click', function() {
        infoPanel.classList.toggle('hidden');
    });

    // 发送聊天消息
    function sendMessage() {
        if (!currentStatus) {
            alert('请先创建女友');
            return;
        }
        const msg = messageInput.value.trim();
        if (!msg) return;
        addMessage('你', msg);
        messageInput.value = '';

        fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'chat',
                params: { message: msg }
            })
        })
        .then(res => res.json())
        .then(handleActionResponse);
    }

    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    // 事件按钮
    document.querySelectorAll('.event').forEach(btn => {
        btn.addEventListener('click', function() {
            if (!currentStatus) {
                alert('请先创建女友');
                return;
            }
            const action = this.dataset.action;
            let params = {};
            if (action === 'gift') {
                params.gift = this.dataset.gift;
            } else if (action === 'date') {
                const place = prompt('选择地点：电影院、餐厅、公园、游乐园、海边', '餐厅');
                if (!place) return;
                params.place = place;
            } else if (action === 'quarrel') {
                const reason = prompt('吵架原因（可选）', '');
                params.reason = reason;
            } else if (action === 'surprise') {
                const st = prompt('惊喜内容（如生日派对）', '惊喜');
                if (!st) return;
                params.surprise_type = st;
            } else if (action === 'festival') {
                const fest = prompt('节日名称', '情人节');
                if (!fest) return;
                params.festival = fest;
            } else if (action === 'propose') {
                // 无需参数
            }

            fetch('/api/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, params })
            })
            .then(res => res.json())
            .then(handleActionResponse);
        });
    });

    // 改名
    renameBtn.addEventListener('click', function() {
        if (!currentStatus) return;
        const newName = prompt('输入新名字', currentStatus.name);
        if (newName && newName.trim()) {
            fetch('/api/rename', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_name: newName.trim() })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    currentStatus = data.status;
                    updateStatus();
                    addMessage('系统', `你为她改名为 ${newName}`);
                }
            });
        }
    });

    // 重新相亲
    resetBtn.addEventListener('click', function() {
        if (!confirm('确定要重新相亲吗？当前进度将丢失。')) return;
        fetch('/api/reset', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // 清除本地状态
                    currentStatus = null;
                    gfName.textContent = '未选择女友';
                    statusPanel.innerHTML = '';
                    chatHistory.innerHTML = '';
                    infoPanel.classList.add('hidden');
                    stopAutoSave();
                    // 显示创建模态框
                    createModal.classList.add('show');
                } else {
                    alert('重置失败');
                }
            });
    });

    // 处理互动响应
    function handleActionResponse(data) {
        if (data.error) {
            alert('错误：' + data.error);
            return;
        }
        if (data.response) {
            addMessage(currentStatus.name, data.response);
        }
        if (data.baby_event) {
            addMessage('系统', data.baby_event);
            alert(data.baby_event);
        }
        currentStatus = data.status;
        updateStatus();
    }

    // 添加消息到历史
    function addMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message';
        if (sender === '你') msgDiv.classList.add('player');
        else if (sender === '系统') msgDiv.classList.add('system');
        else msgDiv.classList.add('girlfriend');
        msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    // 更新状态面板和顶部名字
    function updateStatus() {
        if (!currentStatus) return;
        gfName.textContent = currentStatus.name;
        const lines = [
            `姓名：${currentStatus.name}`,
            `年龄：${currentStatus.age} 岁`,
            `身高：${currentStatus.height} cm`,
            `体重：${currentStatus.weight} kg`,
            `发型：${currentStatus.hair_style}`,
            `脸型：${currentStatus.face_shape}`,
            `职业：${currentStatus.profession}`,
            `性格：${currentStatus.personality}`,
            `着装：${currentStatus.clothes}`,
            `关系：${currentStatus.stage}`,
            `好感度：${currentStatus.affection}`,
            `相处时间：${currentStatus.total_interaction_time} 分钟`
        ];
        statusPanel.innerHTML = lines.join('<br>');
    }

    // 测试连接
    testConnectionBtn.addEventListener('click', function() {
        const apiConfig = {
            api_key: document.getElementById('apiKey').value,
            model: document.getElementById('apiModel').value,
            base_url: document.getElementById('apiBaseUrl').value,
            temperature: parseFloat(document.getElementById('apiTemperature').value),
            max_tokens: parseInt(document.getElementById('apiMaxTokens').value)
        };
        connectionResult.innerHTML = '正在测试连接...';
        connectionResult.className = 'connection-result';
        fetch('/api/test_connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_config: apiConfig })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                connectionResult.innerHTML = '✅ 连接成功！' + (data.message ? ' ' + data.message : '');
                connectionResult.className = 'connection-result success';
            } else {
                connectionResult.innerHTML = '❌ 连接失败：' + (data.error || '未知错误');
                connectionResult.className = 'connection-result error';
            }
        })
        .catch(err => {
            connectionResult.innerHTML = '❌ 请求出错：' + err.message;
            connectionResult.className = 'connection-result error';
        });
    });

    // 提交创建表单
    createForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const useApi = useApiCreate.checked;
        const apiConfig = {
            api_key: document.getElementById('apiKey').value,
            model: document.getElementById('apiModel').value,
            base_url: document.getElementById('apiBaseUrl').value,
            temperature: parseFloat(document.getElementById('apiTemperature').value),
            max_tokens: parseInt(document.getElementById('apiMaxTokens').value)
        };

        // 如果使用API，必须填写API Key（简单校验）
        if (useApi && !apiConfig.api_key) {
            alert('请输入API Key');
            return;
        }

        const formData = {
            profession: document.getElementById('profession').value,
            age: parseInt(document.getElementById('age').value),
            name: document.getElementById('name').value,
            height: parseInt(document.getElementById('height').value),
            weight: parseInt(document.getElementById('weight').value),
            hair_style: document.getElementById('hairStyle').value,
            face_shape: document.getElementById('faceShape').value,
            base_personality: document.getElementById('personality').value,
            use_api: useApi,
            api_config: useApi ? apiConfig : null
        };

        fetch('/api/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentStatus = data.status;
                updateStatus();
                addMessage('系统', `你选择了 ${currentStatus.name}，她${currentStatus.age}岁，是一名${currentStatus.profession}，穿着${currentStatus.clothes}。`);
                createModal.classList.remove('show');
                // 存储API配置到全局变量
                apiConfig = formData.api_config;
                startAutoSave(); // 启动自动保存
            } else {
                alert('创建失败');
            }
        });
    });

    // 设置按钮
    settingsBtn.addEventListener('click', function() {
        // 加载当前配置
        fetch('/api/settings')
            .then(res => res.json())
            .then(config => {
                document.getElementById('settingsApiKey').value = '';
                document.getElementById('settingsApiModel').value = config.model || 'deepseek-chat';
                document.getElementById('settingsApiBaseUrl').value = config.base_url || 'https://api.deepseek.com/v1/chat/completions';
                document.getElementById('settingsApiTemperature').value = config.temperature || 0.8;
                document.getElementById('settingsApiMaxTokens').value = config.max_tokens || 200;
                settingsModal.classList.add('show');
            })
            .catch(err => {
                alert('无法加载API设置');
            });
    });

    // 提交设置
    settingsForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const newConfig = {
            api_key: document.getElementById('settingsApiKey').value,
            model: document.getElementById('settingsApiModel').value,
            base_url: document.getElementById('settingsApiBaseUrl').value,
            temperature: parseFloat(document.getElementById('settingsApiTemperature').value),
            max_tokens: parseInt(document.getElementById('settingsApiMaxTokens').value)
        };
        fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_config: newConfig })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('设置已保存');
                settingsModal.classList.remove('show');
            } else {
                alert('保存失败：' + data.error);
            }
        });
    });

    // 页面关闭前停止定时器（可选）
    window.addEventListener('beforeunload', function() {
        if (saveTimer) clearInterval(saveTimer);
    });
});