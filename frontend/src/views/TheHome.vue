<template>
    <div>
        <h2>Welcome to IESCP!</h2>
        <hr />
        <p>
            IESCP (Influencer Engagement and Sponsorship Coordination Platform) is a one-stop platform to connect
            Sponsors
            and Influencers so that sponsors can get their product/service advertised and influencers can get monetary
            benefits.
        </p>

        <!-- Check if user is authenticated -->
        <template v-if="user.isAuthenticated">
            <p>
                You are logged in as <strong>{{ user.username }}</strong>. ({{ user.userType }})
            </p>
            <router-link :to="`/${user.userType}/dashboard`" class="btn btn-warning">
                {{ capitalize(user.userType) }} Dashboard
            </router-link>
        </template>
        <template v-else>
            <p>To proceed, login or register.</p>
            <div class="btn-group" role="group">
                <router-link to="/login" class="btn btn-success">Login</router-link>
                <router-link to="/register" class="btn btn-warning">Register</router-link>
            </div>
        </template>
    </div>
</template>

<script>
export default {
    name: "TheHome",
    data() {
        return {
            // Mock user data; replace with real data from a store or API
            user: {
                isAuthenticated: false, // Change to true for testing authenticated state
                username: "JohnDoe",
                userType: "sponsor", // Example: sponsor, influencer, or admin
            },
        };
    },
    methods: {
        capitalize(text) {
            return text.charAt(0).toUpperCase() + text.slice(1);
        },
    },
};
</script>

<style scoped>
/* Add any specific styles if needed */
</style>