<template>
    <div>
        <div v-for="(msg, index) in messages" :key="index"
            :class="`alert alert-${msg.category} alert-dismissible fade show`" role="alert">
            {{ msg.message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        messages: {
            type: Array,
            required: false,
        },
    },
};
</script>