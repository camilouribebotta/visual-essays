(window.webpackJsonp=window.webpackJsonp||[]).push([[3],{313:function(t,e,n){"use strict";n(113);var o=n(104);e.a=Object(o.a)("layout")},315:function(t,e,n){"use strict";n.r(e);n(50);var o=n(84),r=n.n(o).a.create({baseURL:"http://localhost:5000"}),c={name:"home",data:function(){return{index:void 0}},mounted:function(){this.getEssay(this.$route.query.src||"https://kg.jstor.org/wiki/Visual_Essays")},methods:{getEssay:function(t){var e=this;r.get("/essay?src=".concat(encodeURIComponent(t),"&nocss")).then((function(t){e.index=t.data}))}},watch:{index:function(){var t=this,e=(this.$route.query.src||"https://kg.jstor.org/wiki/Visual_Essays").split("/"),n=e.slice(0,e.length-1).join("/");this.$nextTick((function(){t.$refs.index.querySelectorAll("a").forEach((function(link){0===link.href.indexOf(n)&&link.addEventListener("click",(function(e){e.preventDefault(),t.$router.push({path:"/essay",query:{src:link.href}})}))}))}))}}},h=n(65),l=n(131),d=n.n(l),f=n(303),y=n(313),component=Object(h.a)(c,(function(){var t=this.$createElement,e=this._self._c||t;return e("v-layout",[e("v-flex",[e("div",{ref:"index",attrs:{id:"index"},domProps:{innerHTML:this._s(this.index)}})])],1)}),[],!1,null,null,null);e.default=component.exports;d()(component,{VFlex:f.a,VLayout:y.a})}}]);