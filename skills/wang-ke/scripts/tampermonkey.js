// ==UserScript==
// @name         网课鼠标保持助手
// @namespace    https://github.com/cycleuser/Skills
// @version      1.0.0
// @description  定时在网页上模拟鼠标移动，防止网课平台因鼠标静止/离开暂停视频
// @author       cycleuser
// @match        *://*.chaoxing.com/*
// @match        *://*.xueyin.com/*
// @match        *://*.yuketang.cn/*
// @match        *://*.zhihuishu.com/*
// @match        *://*.icourse163.com/*
// @match        *://*.erya100.com/*
// @match        *://*.uniwallpapers.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // ========== 配置 ==========
    const INTERVAL = 15000;  // 活动间隔（毫秒），默认15秒
    const MOVE_PIXELS = 2;   // 模拟移动像素数
    // =========================

    let count = 0;
    let running = true;

    function simulateMouseMove() {
        if (!running) return;

        // 在 document 上触发 mousemove 事件
        const events = ['mousemove', 'mouseover', 'mouseout'];
        for (const eventType of events) {
            const event = new MouseEvent(eventType, {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: Math.random() * window.innerWidth,
                clientY: Math.random() * window.innerHeight,
                movementX: MOVE_PIXELS,
                movementY: MOVE_PIXELS,
            });
            document.dispatchEvent(event);
        }

        // 在 video 元素上也触发，防止平台只监听 video
        const videos = document.querySelectorAll('video');
        videos.forEach(video => {
            const event = new MouseEvent('mousemove', {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: video.getBoundingClientRect().left + 10,
                clientY: video.getBoundingClientRect().top + 10,
            });
            video.dispatchEvent(event);

            // 确保视频在播放
            if (video.paused) {
                video.play().catch(() => {});
            }
        });

        count++;
        if (count % 10 === 1) {
            console.log(`[网课助手] 第 ${count} 次活动，时间: ${new Date().toLocaleTimeString()}`);
        }
    }

    // 启动定时器
    const timer = setInterval(simulateMouseMove, INTERVAL);
    simulateMouseMove(); // 立即执行一次

    // 页面可见性变化时，模拟 focus 事件
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            console.log('[网课助手] 页面被隐藏，尝试保持活跃...');
            // 触发 focus 事件，骗过失焦检测
            window.dispatchEvent(new Event('focus'));
            document.dispatchEvent(new Event('focus'));
        }
    });

    // 窗口失焦时模拟 focus
    window.addEventListener('blur', () => {
        setTimeout(() => {
            window.dispatchEvent(new Event('focus'));
            document.dispatchEvent(new Event('focusin'));
        }, 100);
    });

    // 控制台控制
    window.wangke = {
        stop: () => { running = false; clearInterval(timer); console.log('[网课助手] 已停止'); },
        start: () => { running = true; setInterval(simulateMouseMove, INTERVAL); console.log('[网课助手] 已启动'); },
        set: (ms) => { clearInterval(timer); setInterval(simulateMouseMove, ms); console.log(`[网课助手] 间隔改为 ${ms}ms`); },
        count: () => console.log(`[网课助手] 已活动 ${count} 次`),
    };

    console.log('%c网课鼠标保持助手已启动', 'color: #4CAF50; font-size: 14px; font-weight: bold;');
    console.log(`%c间隔: ${INTERVAL}ms | 控制台输入 wangke.stop() 停止`, 'color: #2196F3;');
    console.log('%c仅用于保持自有账号网课播放活跃，请遵守平台使用规范', 'color: #FF9800;');
})();