import re

def apply_fixes(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add cloudDataPromise definition and replace loadCloudData()
    old_load = """        async function loadCloudData() {
            if (!sessionData) return;
            const { data } = await sb.from('anime_users').select('*').eq('id', sessionData.user.id).maybeSingle();
            if (data) {
                app.xmlLib = data.watchlist || [];
                app.recent = data.recent || [];
                if (data.settings) {
                    app.defaultAudio = data.settings.defaultAudio || 'sub'; app.mode = app.defaultAudio;
                    app.server = data.settings.server || 'megaplay';
                    app.user = data.settings.user || app.user; app.showContinue = data.settings.showContinue !== false;
                    app.lang = data.settings.lang || 'english'; app.autoPlay = data.settings.autoPlay !== false;
                    app.autoNext = data.settings.autoNext !== false; app.autoSkipIntro = data.settings.autoSkipIntro === true;
                    app.skipSeconds = parseInt(data.settings.skipSeconds || '85'); app.autoDubFallback = data.settings.autoDubFallback !== false;
                    app.anilistToken = data.settings.anilistToken || null;
                    if (app.anilistToken) {
                        fetchAniListProfile().then(() => {
                            window.syncAniListListToLocal(false);
                        });
                    }
                }
            } else {
                app.user = sessionData.user.email.split('@')[0];
                await sb.from('anime_users').insert([{ id: sessionData.user.id, username: app.user, watchlist: [], recent: [] }]);
            }
            document.getElementById('app-header').classList.remove('hidden');
            document.getElementById('app-navigation').classList.remove('hidden');
            render();

            // Check for pending AniList token saved during startup
            const storedToken = localStorage.getItem('pending_anilist_token');
            if (storedToken) {
                localStorage.removeItem('pending_anilist_token');
                await verifyAndSaveAniListToken(storedToken);
            }
        }"""

    new_load = """        let cloudDataPromise = null;
        async function loadCloudData() {
            if (!sessionData) return;
            if (cloudDataPromise) return cloudDataPromise;

            cloudDataPromise = (async () => {
                try {
                    const { data } = await sb.from('anime_users').select('*').eq('id', sessionData.user.id).maybeSingle();
                    if (data) {
                        app.xmlLib = data.watchlist || [];
                        app.recent = data.recent || [];
                        if (data.settings) {
                            app.defaultAudio = data.settings.defaultAudio || 'sub'; app.mode = app.defaultAudio;
                            app.server = data.settings.server || 'megaplay';
                            app.user = data.settings.user || app.user; app.showContinue = data.settings.showContinue !== false;
                            app.lang = data.settings.lang || 'english'; app.autoPlay = data.settings.autoPlay !== false;
                            app.autoNext = data.settings.autoNext !== false; app.autoSkipIntro = data.settings.autoSkipIntro === true;
                            app.skipSeconds = parseInt(data.settings.skipSeconds || '85'); app.autoDubFallback = data.settings.autoDubFallback !== false;
                            app.anilistToken = data.settings.anilistToken || null;
                            if (app.anilistToken) {
                                fetchAniListProfile().then(() => {
                                    render();
                                });
                            }
                        }
                    } else {
                        app.user = sessionData.user.email.split('@')[0];
                        await sb.from('anime_users').insert([{ id: sessionData.user.id, username: app.user, watchlist: [], recent: [], settings: { user: app.user, server: 'megaplay' } }]);
                    }
                    document.getElementById('app-header').classList.remove('hidden');
                    document.getElementById('app-navigation').classList.remove('hidden');
                    render();

                    // Check for pending AniList token saved during startup
                    const storedToken = localStorage.getItem('pending_anilist_token');
                    if (storedToken) {
                        localStorage.removeItem('pending_anilist_token');
                        await verifyAndSaveAniListToken(storedToken);
                    }
                } catch (e) {
                    console.error("Error loading cloud data:", e);
                }
            })();

            return cloudDataPromise;
        }"""

    # 2. Update window.logout
    old_logout = "window.logout = async function() { await sb.auth.signOut(); sessionData = null; window.location.hash = ''; showLoginPage('login'); };"
    new_logout = """window.logout = async function() {
            await sb.auth.signOut();
            sessionData = null;
            cloudDataPromise = null;
            window.location.hash = '';
            showLoginPage('login');
        };"""

    # 3. Replace verifyAndSaveAniListToken and window.syncAniListListToLocal
    old_verify = """        async function verifyAndSaveAniListToken(token) {
            app.anilistToken = token;
            const res = await gql(`query { Viewer { id name avatar { large } } }`);
            if (res && res.data && res.data.Viewer) {
                app.anilistProfile = {
                    name: res.data.Viewer.name,
                    avatar: res.data.Viewer.avatar.large
                };
                saveCloudData();
                window.showToast(`Welkom, ${res.data.Viewer.name}! Gekoppeld met AniList.`);
                await window.syncAniListListToLocal(true);
            } else {
                app.anilistToken = null;
                app.anilistProfile = null;
                window.showToast("Ongeldige AniList Token. Probeer opnieuw.", "error");
            }
        }"""

    new_verify = """        async function verifyAndSaveAniListToken(token) {
            app.anilistToken = token;
            const res = await gql(`query { Viewer { id name avatar { large } } }`);
            if (res && res.data && res.data.Viewer) {
                app.anilistProfile = {
                    name: res.data.Viewer.name,
                    avatar: res.data.Viewer.avatar.large
                };
                await saveCloudData();
                window.showToast(`Welkom, ${res.data.Viewer.name}! Gekoppeld met AniList.`);
                await window.syncAniListListToLocal(true);
            } else {
                app.anilistToken = null;
                app.anilistProfile = null;
                window.showToast("Ongeldige AniList Token. Probeer opnieuw.", "error");
            }
        }"""

    old_sync = """        window.syncAniListListToLocal = async function(manualToast = true) {
            if (!app.anilistToken) {
                if (manualToast) window.showToast("Log eerst in met AniList!", "error");
                return;
            }
            if (manualToast) window.showToast("AniList lijst ophalen...");

            try {
                const viewerRes = await gql(`query { Viewer { id name avatar { large } } }`);
                if (!viewerRes || !viewerRes.data || !viewerRes.data.Viewer) {
                    if (manualToast) window.showToast("Kon AniList profiel niet ophalen.", "error");
                    return;
                }
                const viewer = viewerRes.data.Viewer;
                app.anilistProfile = {
                    name: viewer.name,
                    avatar: viewer.avatar.large
                };

                const listRes = await gql(`
                    query ($userId: Int) {
                        MediaListCollection(userId: $userId, type: ANIME) {
                            lists {
                                name
                                status
                                entries {
                                    id
                                    status
                                    progress
                                    media {
                                        id
                                        title {
                                            romaji
                                            english
                                        }
                                        episodes
                                        coverImage {
                                            large
                                        }
                                    }
                                }
                            }
                        }
                    }
                `, { userId: viewer.id });

                if (!listRes || !listRes.data || !listRes.data.MediaListCollection) {
                    if (manualToast) window.showToast("Kon AniList lijst niet ophalen.", "error");
                    return;
                }

                const lists = listRes.data.MediaListCollection.lists;
                const alStatusMap = {
                    'CURRENT': 'Watching',
                    'PLANNING': 'Plan to Watch',
                    'COMPLETED': 'Watched',
                    'DROPPED': 'Dropped',
                    'PAUSED': 'Watching'
                };

                let updatedCount = 0;
                let addedCount = 0;
                let localLib = [...app.xmlLib];

                lists.forEach(list => {
                    if (!list.entries) return;
                    list.entries.forEach(entry => {
                        const media = entry.media;
                        if (!media) return;

                        const mediaIdStr = media.id.toString();
                        const alStatus = entry.status;
                        const localStatus = alStatusMap[alStatus] || 'Watching';
                        const progress = entry.progress || 0;
                        const episodes = media.episodes || 12;
                        const coverImage = media.coverImage ? media.coverImage.large : '';
                        const title = app.lang === 'english' ? (media.title.english || media.title.romaji) : (media.title.romaji || media.title.english);

                        const existingIdx = localLib.findIndex(item => item && item.id.toString() === mediaIdStr);

                        if (existingIdx !== -1) {
                            localLib[existingIdx] = {
                                ...localLib[existingIdx],
                                status: localStatus,
                                progress: progress,
                                episodes: episodes,
                                coverImage: coverImage || localLib[existingIdx].coverImage,
                                title: title || localLib[existingIdx].title
                            };
                            updatedCount++;
                        } else {
                            localLib.push({
                                id: mediaIdStr,
                                title: title,
                                status: localStatus,
                                progress: progress,
                                episodes: episodes,
                                coverImage: coverImage
                            });
                            addedCount++;
                        }
                    });
                });

                app.xmlLib = localLib;
                await saveCloudData();
                render();

                if (manualToast) {
                    window.showToast(`Succesvol gesynchroniseerd! ${addedCount} toegevoegd, ${updatedCount} bijgewerkt.`, "success");
                }
            } catch (e) {
                console.error("Fout tijdens AniList sync:", e);
                if (manualToast) window.showToast("Fout bij synchroniseren met AniList.", "error");
            }
        };"""

    new_sync = """        window.syncAniListListToLocal = async function(manualToast = true) {
            if (!app.anilistToken) {
                if (manualToast) window.showToast("Log eerst in met AniList!", "error");
                return;
            }
            if (manualToast) window.showToast("AniList bibliotheek synchroniseren...");

            try {
                const viewerRes = await gql(`query { Viewer { id name avatar { large } } }`);
                if (!viewerRes || !viewerRes.data || !viewerRes.data.Viewer) {
                    if (manualToast) window.showToast("Kon AniList profiel niet ophalen.", "error");
                    return;
                }
                const viewer = viewerRes.data.Viewer;
                app.anilistProfile = {
                    name: viewer.name,
                    avatar: viewer.avatar.large
                };

                const listRes = await gql(`
                    query ($userId: Int) {
                        MediaListCollection(userId: $userId, type: ANIME) {
                            lists {
                                name
                                status
                                entries {
                                    id
                                    status
                                    progress
                                    media {
                                        id
                                        title {
                                            romaji
                                            english
                                        }
                                        episodes
                                        coverImage {
                                            large
                                        }
                                    }
                                }
                            }
                        }
                    }
                `, { userId: viewer.id });

                if (!listRes || !listRes.data || !listRes.data.MediaListCollection) {
                    if (manualToast) window.showToast("Kon AniList lijst niet ophalen.", "error");
                    return;
                }

                const lists = listRes.data.MediaListCollection.lists;
                const aniListEntries = [];
                lists.forEach(list => {
                    if (list.entries) {
                        list.entries.forEach(entry => {
                            if (entry && entry.media) {
                                aniListEntries.push(entry);
                            }
                        });
                    }
                });

                const alStatusMap = {
                    'CURRENT': 'Watching',
                    'PLANNING': 'Plan to Watch',
                    'COMPLETED': 'Watched',
                    'DROPPED': 'Dropped',
                    'PAUSED': 'Watching'
                };

                const localToAlStatusMap = {
                    'Watching': 'CURRENT',
                    'Plan to Watch': 'PLANNING',
                    'Watched': 'COMPLETED',
                    'Completed': 'COMPLETED',
                    'Dropped': 'DROPPED'
                };

                let localLib = [...app.xmlLib];
                const aniListMap = {};
                aniListEntries.forEach(entry => {
                    aniListMap[entry.media.id.toString()] = entry;
                });

                const toPushToAniList = [];
                let pulledCount = 0;

                // 1. Process existing local items against AniList
                localLib = localLib.map(localItem => {
                    if (!localItem || !localItem.id) return localItem;
                    const mediaIdStr = localItem.id.toString();
                    const aniItem = aniListMap[mediaIdStr];

                    if (aniItem) {
                        const aniProgress = aniItem.progress || 0;
                        const localProgress = localItem.progress || 0;

                        if (localProgress > aniProgress) {
                            // Local is ahead. Push to AniList.
                            toPushToAniList.push({
                                id: mediaIdStr,
                                progress: localProgress,
                                status: localToAlStatusMap[localItem.status] || 'CURRENT'
                            });
                            return localItem;
                        } else if (aniProgress > localProgress) {
                            // AniList is ahead. Pull to local.
                            pulledCount++;
                            return {
                                ...localItem,
                                progress: aniProgress,
                                status: alStatusMap[aniItem.status] || 'Watching'
                            };
                        } else {
                            // Progress is equal. Align status.
                            const mappedAniStatus = alStatusMap[aniItem.status] || 'Watching';
                            if (localItem.status !== mappedAniStatus) {
                                if (localItem.status === 'Watched' || localItem.status === 'Completed') {
                                    toPushToAniList.push({
                                        id: mediaIdStr,
                                        progress: localProgress,
                                        status: 'COMPLETED'
                                    });
                                    return localItem;
                                } else if (mappedAniStatus === 'Watched' || mappedAniStatus === 'Completed') {
                                    pulledCount++;
                                    return {
                                        ...localItem,
                                        status: 'Watched'
                                    };
                                } else {
                                    pulledCount++;
                                    return {
                                        ...localItem,
                                        status: mappedAniStatus
                                    };
                                }
                            }
                            return localItem;
                        }
                    } else {
                        // Local-only. Push to AniList.
                        toPushToAniList.push({
                            id: mediaIdStr,
                            progress: localItem.progress || 0,
                            status: localToAlStatusMap[localItem.status] || 'CURRENT'
                        });
                        return localItem;
                    }
                });

                // 2. Add AniList-only items to local
                aniListEntries.forEach(entry => {
                    const mediaIdStr = entry.media.id.toString();
                    const existsLocally = localLib.some(item => item && item.id.toString() === mediaIdStr);

                    if (!existsLocally) {
                        const media = entry.media;
                        const title = app.lang === 'english' ? (media.title.english || media.title.romaji) : (media.title.romaji || media.title.english);
                        localLib.push({
                            id: mediaIdStr,
                            title: title,
                            status: alStatusMap[entry.status] || 'Watching',
                            progress: entry.progress || 0,
                            episodes: media.episodes || 12,
                            coverImage: media.coverImage ? media.coverImage.large : ''
                        });
                        pulledCount++;
                    }
                });

                // 3. Push local changes to AniList
                let pushedCount = 0;
                if (toPushToAniList.length > 0) {
                    for (const item of toPushToAniList) {
                        try {
                            const mutation = `mutation ($mediaId: Int, $progress: Int, $status: MediaListStatus) { SaveMediaListEntry (mediaId: $mediaId, progress: $progress, status: $status) { id status progress } }`;
                            await gql(mutation, {
                                mediaId: parseInt(item.id),
                                progress: parseInt(item.progress),
                                status: item.status
                            });
                            pushedCount++;
                        } catch (err) {
                            console.error(`Fout bij pushen van item ${item.id} naar AniList:`, err);
                        }
                    }
                }

                app.xmlLib = localLib;
                await saveCloudData();
                render();

                if (manualToast) {
                    window.showToast(`Sync voltooid! ${pulledCount} binnengehaald, ${pushedCount} gepusht naar AniList.`, "success");
                }
            } catch (e) {
                console.error("Fout tijdens AniList sync:", e);
                if (manualToast) window.showToast("Fout bij synchroniseren met AniList.", "error");
            }
        };"""

    # 4. Check & replace
    modified = False

    if old_load in content:
        content = content.replace(old_load, new_load)
        print(f"Successfully replaced old_load in {filename}")
        modified = True
    else:
        # Try looser matching
        print(f"Warning: Exact old_load match not found in {filename}")

    if old_logout in content:
        content = content.replace(old_logout, new_logout)
        print(f"Successfully replaced old_logout in {filename}")
        modified = True
    else:
        print(f"Warning: Exact old_logout match not found in {filename}")

    if old_verify in content:
        content = content.replace(old_verify, new_verify)
        print(f"Successfully replaced old_verify in {filename}")
        modified = True
    else:
        print(f"Warning: Exact old_verify match not found in {filename}")

    if old_sync in content:
        content = content.replace(old_sync, new_sync)
        print(f"Successfully replaced old_sync in {filename}")
        modified = True
    else:
        print(f"Warning: Exact old_sync match not found in {filename}")

    if modified:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved changes to {filename}")
    else:
        print(f"No changes made to {filename}")

apply_fixes('jules.html')
apply_fixes('index.html')
