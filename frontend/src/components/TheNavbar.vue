<template>
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
        <div class="container-fluid">
            <router-link class="navbar-brand" to="/">IESCP</router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarScroll"
                aria-controls="navbarScroll" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarScroll">
                <ul class="navbar-nav ms-auto my-2 my-lg-0 navbar-nav-scroll" style="--bs-scroll-height: 100px;">
                    <template v-if="user.isAuthenticated">
                        <template v-if="user.userType === 'sponsor'">
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/sponsor/dashboard">Dashboard</router-link></li>
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/sponsor/campaigns">Campaigns</router-link></li>
                            <li class="nav-item"><router-link class="nav-link" to="/sponsor/find">Find</router-link>
                            </li>
                            <li class="nav-item"><router-link class="nav-link" to="/sponsor/stats">Stats</router-link>
                            </li>
                        </template>
                        <template v-else-if="user.userType === 'influencer'">
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/influencer/dashboard">Dashboard</router-link></li>
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/influencer/find-campaigns">Find</router-link></li>
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/influencer/stats">Stats</router-link></li>
                        </template>
                        <template v-else-if="user.userType === 'admin'">
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/admin/dashboard">Dashboard</router-link></li>
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/admin/supervise">Campaigns</router-link></li>
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/admin/find-influencers">Influencers</router-link></li>
                            <li class="nav-item"><router-link class="nav-link"
                                    to="/admin/find-sponsors">Sponsors</router-link></li>
                        </template>
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown"
                                aria-expanded="false">
                                <b>{{ user.username }}</b>
                            </a>
                            <ul class="dropdown-menu">
                                <li><router-link class="dropdown-item" to="/edit-profile">Edit Profile</router-link>
                                </li>
                            </ul>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link text-danger" href="#" @click="logout">Logout</a>
                        </li>
                    </template>
                    <template v-else>
                        <li class="nav-item"><router-link class="nav-link" to="/login">Login</router-link></li>
                        <li class="nav-item"><router-link class="nav-link" to="/register">Register</router-link></li>
                    </template>
                </ul>
            </div>
        </div>
    </nav>
</template>

<script>
export default {
    data() {
        return {
            user: {
                isAuthenticated: true,
                username: "JohnDoe",
                userType: "sponsor", // Could be sponsor, influencer, or admin
            },
        };
    },
    methods: {
        logout() {
            // Implement logout functionality
            console.log("User logged out");
        },
    },
};
</script>