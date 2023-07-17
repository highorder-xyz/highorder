<script lang="ts">
import { defineComponent, reactive } from 'vue'
import gsap from "gsap";

export default defineComponent({
    props: {
        scale: { type: Number, default: 1 }
    },
    methods: {

    },
    mounted() {
        gsap.set([this.$refs.left_eye_open, this.$refs.right_eye_open],{
            opacity: 0,
            scale: 1.2,
            transformOrigin: "center",
        });
        gsap.to([this.$refs.left_hand],{
            rotate: -15,
            transformOrigin: "top",
            repeat: -1,
            yoyo: true,
            duration: 2,
            ease: "power1.inOut"
        });

        // let tail = gsap.timeline({ repeat: -1, yoyo: true, });

        // tail.to([this.$refs.tail], {
        //     ease: "power1.in",
        //     morphSVG: { shape: "M447.606 379.471v51.687" },
        //     duration: 1,
        //     delay: 2
        // })
        //     .to([this.$refs.tail], {
        //         ease: "power1.out",
        //         duration: 1,
        //         morphSVG: { shape: "M447.606 379.471v24.772s.061 26.915 28.211 26.915" }
        //     });
    }
})

</script>

<template>
    <div class="catbox" :style="`width:${240*scale}px;height:${140*scale}px`">
        <svg :width="`${59.310059*scale}mm`" :height="`${25.015484*scale}mm`" viewBox="0 0 59.310059 25.015484" version="1.1" id="svg5"
            xml:space="preserve" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
            <defs id="defs2" />
            <g id="layer1" transform="translate(-3.4266501,-2.9303767)">
                <g style="clip-rule:evenodd;fill-rule:evenodd;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:1.5"
                    id="g185" transform="matrix(0.26458333,0,0,0.26458333,-72.751653,-87.983442)">
                    <g id="window">
                        <path id="window__base" fill="#627271" d="m 287.918,401.069 h 224.164 v 22.23 H 287.918 Z" />
                        <g id="g134">
                            <path id="right-hand"
                                d="m 331.488,386.954 c 0,0 -27.273,-1.471 -26.23,7.167 0.766,6.338 8.295,7.357 14.469,7.772 6.174,0.416 36.055,0.929 11.761,-14.939 z"
                                fill="#F59E5B" />
                            <path id="body"
                                d="m 352.39,365.252 c 0,0 81.405,-40.993 98.905,-0.68 11.659,26.856 -7.929,42.029 -43.527,42.029 -23.361,0 -43.863,-1.589 -52.67,-5.837 -8.806,-4.248 -2.708,-35.512 -2.708,-35.512 z"
                                fill="#F59E5B" />
                            <clipPath id="_clip2">
                                <path
                                    d="m 352.39,365.252 c 0,0 81.405,-40.993 98.905,-0.68 11.659,26.856 -7.929,42.029 -43.527,42.029 -23.361,0 -43.863,-1.589 -52.67,-5.837 -8.806,-4.248 -2.708,-35.512 -2.708,-35.512 z"
                                    id="path79" />
                            </clipPath>
                            <g clip-path="url(#_clip2)" fill="#EE7729" id="g88">
                                <ellipse cx="387.298" cy="348.073" rx="6.7449999" ry="21.523001" id="ellipse82" />
                                <ellipse cx="405.01001" cy="345.617" rx="6.7449999" ry="21.523001" id="ellipse84" />
                                <ellipse cx="421.30899" cy="342.36401" rx="6.7449999" ry="21.523001" id="ellipse86" />
                            </g>
                            <g id="face">
                                <path
                                    d="m 364.317,400.424 c 0,0 11.226,-4.284 15.647,-9.691 6.564,-8.027 3.892,-15.747 3.892,-15.747 l -11.031,0.387 z"
                                    fill="#303853" fill-opacity="0.2" id="path90" />
                                <path id="head"
                                    d="m 351,346.994 c 18.134,0 32.856,12.256 32.856,27.351 0,15.096 -5.681,27.352 -32.856,27.352 -27.175,0 -32.856,-12.256 -32.856,-27.352 0,-15.095 14.722,-27.351 32.856,-27.351 z"
                                    fill="#F59E5B" />
                                <clipPath id="_clip3">
                                    <path id="head1"
                                        d="m 351,346.994 c 18.134,0 32.856,12.256 32.856,27.351 0,15.096 -5.681,27.352 -32.856,27.352 -27.175,0 -32.856,-12.256 -32.856,-27.352 0,-15.095 14.722,-27.351 32.856,-27.351 z" />
                                </clipPath>
                                <g clip-path="url(#_clip3)" id="g96">
                                    <ellipse id="head__mark" cx="352.146" cy="341.55899" rx="6.7379999" ry="21.523001"
                                        fill="#EE7729" />
                                </g>
                                <g id="ear__left">
                                    <path
                                        d="m 329.297,344.831 c 1.229,-1.448 3.397,-1.633 4.854,-0.414 5.049,4.184 8.243,8.982 9.656,14.354 0.415,1.603 -0.359,3.277 -1.849,4 -5.62,2.725 -11.188,3.166 -16.711,1.657 -1.627,-0.446 -2.699,-1.995 -2.544,-3.675 0.628,-6.08 2.837,-11.38 6.594,-15.922 z"
                                        fill="#F59E5B" id="path98" />
                                    <path
                                        d="m 329.582,351.25 a 3.3964,3.3964 0 0 1 2.573,-1.627 c 1.066,-0.106 2.12,0.298 2.843,1.088 1.11,1.065 1.923,2.266 2.509,3.539 a 3.4906,3.4906 0 0 1 -2.203,4.826 c -1.44,0.422 -2.872,0.558 -4.298,0.426 a 3.4897,3.4897 0 0 1 -2.508,-1.416 3.4889,3.4889 0 0 1 -0.591,-2.819 c 0.411,-1.425 0.944,-2.769 1.675,-4.017 z"
                                        fill="#d7edee" id="path100" />
                                </g>
                                <g id="ear__right">
                                    <path
                                        d="m 371.927,344.794 c 1.657,-0.929 3.754,-0.346 4.693,1.305 3.274,5.682 4.595,11.292 4.046,16.819 -0.17,1.648 -1.479,2.947 -3.127,3.105 -6.218,0.595 -11.591,-0.934 -16.241,-4.274 -1.369,-0.985 -1.834,-2.811 -1.103,-4.331 2.709,-5.48 6.627,-9.677 11.732,-12.624 z"
                                        fill="#F59E5B" id="path103" />
                                    <path
                                        d="m 370.019,350.745 a 3.3997,3.3997 0 0 1 2.96,-0.605 3.3971,3.3971 0 0 1 2.273,1.991 c 0.726,1.497 1.094,3.016 1.194,4.522 a 3.4903,3.4903 0 0 1 -3.717,3.729 c -1.618,-0.099 -3.114,-0.5 -4.498,-1.183 a 3.491,3.491 0 0 1 -1.832,-2.189 c -0.271,-0.957 -0.12,-1.985 0.415,-2.824 0.936,-1.303 1.984,-2.463 3.205,-3.441 z"
                                        fill="#d7edee" id="path105" />
                                </g>
                                <g id="face__details">
                                    <path d="m 336.292,387.714 c 0,0 -4.319,-1.775 -9.465,-0.34" fill="none"
                                        stroke="#556f80" stroke-width="2" id="path108" />
                                    <path d="m 362.652,387.714 c 0,0 4.319,-1.775 9.465,-0.34" fill="none"
                                        stroke="#556f80" stroke-width="2" id="path110" />
                                    <path d="m 336.575,390.032 c 0,0 -3.765,-0.486 -8.735,2.944" fill="none"
                                        stroke="#556f80" stroke-width="2" id="path112" />
                                    <path d="m 362.369,390.032 c 0,0 3.765,-0.486 8.735,2.944" fill="none"
                                        stroke="#556f80" stroke-width="2" id="path114" />
                                    <path
                                        d="m 349.873,386.424 c 0.392,-0.242 0.89,-0.232 1.273,0.025 0.165,0.106 0.317,0.227 0.457,0.355 0.443,0.399 0.599,1.027 0.393,1.586 -0.206,0.56 -0.732,0.937 -1.327,0.953 a 6.271,6.271 0 0 1 -0.434,-0.01 1.4684,1.4684 0 0 1 -0.872,-2.576 c 0.164,-0.108 0.329,-0.224 0.51,-0.333 z"
                                        fill="#556f80" id="path116" />
                                    <path id="eye__left__close"
                                        d="m 332.463,377.656 c 0.993,1.432 3.476,2.14 5.122,2.13 1.987,-0.011 4.014,-0.609 5.028,-2.13"
                                        fill="none" stroke="#556f80" stroke-width="2" />
                                    <path id="eye__right__close"
                                        d="m 357.174,377.656 c 0.992,1.432 3.475,2.14 5.121,2.13 1.987,-0.011 4.015,-0.609 5.028,-2.13"
                                        fill="none" stroke="#556f80" stroke-width="2" />
                                    <g id="eye__right__open" ref="right_eye_open">
                                        <ellipse cx="362.19601" cy="377.815" rx="4.9419999" ry="6.5149999"
                                            fill="#d7edee" id="ellipse120" />
                                        <ellipse id="eye__right__open__p" cx="362.19601" cy="377.815" rx="3.5599999"
                                            ry="4.8200002" fill="#556f80" />
                                    </g>
                                    <g id="eye__left__open" ref="left_eye_open">
                                        <ellipse cx="337.56601" cy="377.815" rx="4.9419999" ry="6.5149999"
                                            fill="#d7edee" id="ellipse124" />
                                        <ellipse id="eye__left__open__p" cx="337.56601" cy="377.815" rx="3.5599999"
                                            ry="4.8200002" fill="#556f80" />
                                    </g>
                                </g>
                            </g>
                            <path id="leg"
                                d="m 434.587,386.268 c 0,0 41.571,-0.431 39.44,10.421 -1.563,7.963 -13.079,8.856 -22.495,9.058 -9.416,0.202 -54.893,-0.712 -16.945,-19.479 z"
                                fill="#F59E5B" />
                            <g id="tails" fill="none" stroke="#F59E5B" stroke-width="14">
                                <!--         <path  d="M447.606 379.471v51.687"/> -->
                                <path id="tail" ref="tail" d="m 447.606,379.471 v 24.772 c 0,0 -0.061,26.915 -28.211,26.915" />
                                <!--         <path d="M447.606 379.471v24.772s.061 26.915 28.211 26.915"/> -->
                            </g>
                            <path id="left-hand" ref="left_hand"
                                d="m 367.154,392.352 c 0,0 -15.939,22.18 -8.101,25.956 5.751,2.772 10.668,-3.021 14.346,-7.998 3.677,-4.976 20.216,-29.868 -6.245,-17.958 z"
                                fill="#F59E5B" />
                        </g>
                    </g>
                </g>
            </g>
        </svg>

    </div>
</template>

<style  scoped>
.catbox {
    width: 240px;
    height: 140px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto;
}

svg #window {
    cursor: pointer;
}
</style>