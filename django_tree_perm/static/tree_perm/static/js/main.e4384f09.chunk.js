(this.webpackJsonpfrontend=this.webpackJsonpfrontend||[]).push([[0],{198:function(e,t,a){},218:function(e,t,a){"use strict";a.r(t);var n=a(0),s=a.n(n),l=a(185),c=a.n(l),r=a(15),i=a(174),o=a.n(i),d=(a(198),a(233)),u=a(229),j=a(230),h=a(236),b=a(243),p=a(238),O=a(175),m=a.n(O);function x(){let e={},t=0;const a=t=>function(){const a=e,n=a[t];return delete a[t],n?n(...arguments):function(){for(var e=arguments.length,t=new Array(e),a=0;a<e;a++)t[a]=arguments[a];return t}(...arguments)},n=n=>{const s=t++;return e[s]=n,a(s)};return n.unmount=()=>e={},n}function f(){const e=Object(n.useRef)(x());return Object(n.useEffect)((()=>(e.current=x(),()=>{e.current&&e.current.unmount()})),[]),[e.current]}var v=a(239);const g=a(231).a.create({timeout:1e4,headers:{"Content-Type":"application/json"}});g.interceptors.request.use((e=>{const t={...e.headers};if(["POST","PUT","PATCH","DELETE"].includes(e.method.toUpperCase())){var a;let e=null===(a=document.querySelector("[name=csrfmiddlewaretoken]"))||void 0===a?void 0:a.value;e||(e=function(e){let t=null;if(document.cookie&&""!==document.cookie){const a=document.cookie.split(";");for(let n=0;n<a.length;n++){const s=a[n].trim();if(s.substring(0,e.length+1)===e+"="){t=decodeURIComponent(s.substring(e.length+1));break}}}return t}("csrftoken")),t["X-CSRFToken"]=e}return e.headers=t,e})),g.interceptors.response.use((e=>e),(e=>{var t,a;const{errMsg:n}=function(e){let t=e.message;if(e.response){const a=e.response.status;let n="";switch(a){case 401:n="\u672a\u767b\u5f55";break;case 403:n="\u672a\u6388\u6743/\u7981\u6b62\u64cd\u4f5c";break;case 404:n=`${e.config.url}`;break;default:n=e.response.data,n instanceof Object&&(n=JSON.stringify(n))}e.response.status&&(t=`HttpError(${a}): ${n}`)}return{errMsg:t}}(e),s={message:"\u64cd\u4f5c\u5931\u8d25\uff0c\u8bf7\u91cd\u8bd5",description:n};return 401===(null===e||void 0===e||null===(t=e.response)||void 0===t?void 0:t.status)?s.key="401":403===(null===e||void 0===e||null===(a=e.response)||void 0===a?void 0:a.status)&&(s.key="403"),v.a.error(s),Promise.reject(e)}));var y=g;const k=".",S="tree/perm/",E="tree/nodes/",_=e=>`tree/nodes/${e}/`,w="tree/lazyload/",C="tree/load/",D="tree/roles/",$=function(e){let t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:"";return t?`tree/roles/${e}/?node_id=${t}`:`tree/roles/${e}/`},R="tree/noderoles/",L=e=>`tree/noderoles/${e}/`,T="tree/users/",I={labelCol:{flex:"120px"},wrapperCol:{xs:{span:24},sm:{span:18}}},N={width:"50%",destroyOnClose:!0,maskClosable:!0};var z=a(246),F=a(190),A=a(247),U=a(248),P=a(249),M=a(250),q=a(188),H=a(120),K=a(64),V=a(186),W=a(235),J=a(234),B=a(244),Q=a(147),X=a(133),G=a(180),Y=a(9);const Z=e=>(null===e||void 0===e?void 0:e.results)||[],ee=(e,t)=>t?e instanceof Array?e:void 0!==e&&null!==e?[e]:[]:e;var te=e=>{let{value:t,onChange:a,restful:s,genDetailUri:l=null,filters:c=null,searchKey:r="search",parseListResponse:i=Z,initOptions:o,fieldNames:d,disabled:u=!1,mode:j,antdSelectProps:h={}}=e;const[b]=f(),[p,O]=Object(n.useState)("multiple"===j),[m,x]=Object(n.useState)(ee(t,"multiple"===j)),[v,g]=Object(n.useState)(),[k,S]=Object(n.useState)(!1),[E,_]=Object(n.useState)(o||[]),w=Object(n.useRef)(new Set),C=Object(n.useCallback)((e=>e[(null===d||void 0===d?void 0:d.value)||"value"]),[d]),D=Object(n.useCallback)(((e,t)=>{x(e),"function"===typeof a&&a(e,t)}),[a]);Object(n.useEffect)((()=>{O("multiple"===j)}),[j]),Object(n.useEffect)((()=>{x((e=>Object(G.a)(e,t)?e:ee(t,"multiple"===j)))}),[t,j]);const $=Object(n.useMemo)((()=>null===m||void 0===m?[]:p?m:[m]),[m,p]);Object(n.useEffect)((()=>{if(null===m||void 0===m||""===m)return;const e=p?m:[m],t=E.map((e=>C(e))),a=e.filter((e=>!t.includes(e)&&!w.current.has(e)));if(!a.length)return;a.forEach((e=>w.current.add(e)));const n=a.map((e=>y.get("function"===typeof l?l(e):`${s}${e}/`)));Promise.all(n).then(b((e=>{const t=e.map((e=>e.data));_((e=>t.concat(e)))})))}),[b,C,m,p,s,l,E]),Object(n.useEffect)((()=>{if(u||!s||!v)return;const e=setTimeout(b((()=>{let e={...c};v&&(e[r]=v),S(!0),y.get(s,{params:e}).then(b((e=>{const t=i(e.data);_((e=>{const a=e.filter((e=>$.includes(C(e)))),n=a.map((e=>C(e))),s=t.filter((e=>!n.includes(C(e))));return a.concat(s)}))}))).finally(b((()=>S(!1))))})),200);return()=>clearTimeout(e)}),[s,c,r,i,v,b,u,$,C]);const R=Object(n.useMemo)((()=>{let e="\u65e0\u66f4\u591a\u6570\u636e";if(s)return e=k?Object(Y.jsx)(V.a,{size:"small"}):"\u8bf7\u8f93\u5165\u5408\u9002\u7684\u5173\u952e\u5b57\u8fdb\u884c\u641c\u7d22",e}),[s,k]);return Object(Y.jsx)(X.a,{notFoundContent:R,popupMatchSelectWidth:!1,allowClear:!0,placeholder:"\u53ef\u8f93\u5165\u5173\u952e\u5185\u5bb9\u641c\u7d22\uff0c\u4ece\u4e0b\u62c9\u5217\u8868\u4e2d\u9009\u62e9",...h,mode:j,disabled:u,options:E,fieldNames:d,value:m,filterOption:!1,showSearch:!0,onSearch:e=>g(e),onClear:()=>D(null),onChange:(e,t)=>D(e,t)})};const ae=new Q([{key:"REFRESH",value:"refresh",label:"\u52a0\u8f7d\u5b50\u7ed3\u70b9"},{key:"ADD",value:"add",label:"\u65b0\u589e\u5b50\u7ed3\u70b9"},{key:"EDIT",value:"edit",label:"\u4fee\u6539\u4fe1\u606f"},{key:"DELETE",value:"delete",label:"\u5220\u9664\u7ed3\u70b9",danger:!0}]),ne={[ae.REFRESH]:Object(Y.jsx)(z.a,{}),[ae.ADD]:Object(Y.jsx)(F.a,{}),[ae.EDIT]:Object(Y.jsx)(A.a,{}),[ae.DELETE]:Object(Y.jsx)(U.a,{})},se="path",le=(e,t)=>{if(!t)return null;for(let a=0;a<e.length;a++){const n=e[a];if(t&&n.path===t)return n;if(n.children&&t&&n.path&&t.startsWith(`${n.path}${k}`))return le(n.children,t)}return null},ce=function(e){let t=arguments.length>1&&void 0!==arguments[1]&&arguments[1];for(let n=0;n<e.length;n++){var a;const s=e[n];s.is_key?s.isLeaf=!0:!t||null!==(a=s.children)&&void 0!==a&&a.length||(s.isLeaf=!0),s.children&&ce(s.children,t)}},re=(e,t)=>{const a=(e=>{if(!e)return"";const t=e.split(k);return t.length<=1?"":(t.pop(),t.join(k))})(t.path);if(!a)return e.filter((e=>e.id!==t.id));const n=le(e,a);return n&&n.children?(n.children=n.children.filter((e=>e[se]!==t[se])),e):e},ie=e=>e.alias?`${e.name} (${e.alias})`:e.name,oe=e=>{let t=[];for(let n=0;n<e.length;n++){var a;const s=e[n];s.depth<2&&t.push(s[se]),(null===(a=s.children)||void 0===a?void 0:a.length)>0&&(t.push(s[se]),t=t.concat(oe(s.children)))}return t};var de=e=>{let{user:t,defaultValue:a,onChange:s}=e;const[l]=f(),[c,r]=Object(n.useState)(!1),i=Object(n.useRef)(),[o,O]=Object(n.useState)([]),[m,x]=Object(n.useState)(a),[v,g]=Object(n.useState)([]),[S,D]=Object(n.useState)([]),[$,R]=Object(n.useState)(),[L,T]=Object(n.useState)(),[A,U]=Object(n.useState)(!1),[Q]=d.a.useForm(),[X,G]=Object(n.useState)(!1),[Z,ee]=Object(n.useState)(),[de,ue]=Object(n.useState)(),[je,he]=Object(n.useState)(0),be=Object(n.useCallback)(((e,t)=>{e&&(x(e),t||(t=le(o,null,e)),"function"===typeof s&&s(t))}),[s,o]),pe=Object(n.useCallback)(((e,t)=>{const a={};e&&(a.parent_path=e.path),y.get(w,{params:a}).then(l((t=>{const a=t.data.results;O((t=>{const n=((e,t,a)=>{if(!t||0===t.length)return e;if(ce(t),!a)return t;if(0===e.length)return t;const n=le(e,a);return n?(n.children=t,e):e})(t,a,null===e||void 0===e?void 0:e.path);return[...n]})),e&&(g((t=>{const a=t.filter((t=>!t.startsWith(`${e[se]}${k}`)));return a.includes(e[se])||a.push(e[se]),a})),D((t=>{const a=t.filter((t=>!t.startsWith(`${e[se]}${k}`)));return a.includes(e[se])||a.push(e[se]),a})))}))).finally(l((()=>t&&t())))}),[l]),Oe=Object(n.useCallback)((function(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:null;r(!0);const t=!e;y.get(C,{params:e}).then(l((e=>{const a=e.data.results;ce(a,t),O(a);const n=oe(a);g(n),t||D([])}))).finally(l((()=>r(!1))))}),[l]);Object(n.useEffect)((()=>{a&&a.split(k).length>2?ue(a):Oe({depth:2})}),[]),Object(n.useEffect)((()=>{void 0!==de&&null!==de&&setTimeout((()=>{Oe(de?{search:de}:{depth:2})}),200)}),[de,je,Oe]);const me=Object(n.useCallback)((e=>{const t={name:null,alias:"",description:"",parent_id:null,is_key:!1,...e};null===Q||void 0===Q||Q.setFieldsValue(t)}),[Q]),xe=Object(n.useCallback)((e=>{let t={};return e.is_key&&(t.fontWeight="bold",t.color="#fa8c16",de&&e.name.indexOf(de)>-1&&(t.color="#fa541c")),t}),[de]),fe=Object(n.useCallback)((e=>ae.options.filter((t=>!e.is_key||!![ae.EDIT,ae.DELETE].includes(t.value))).map((e=>({...e,key:e.value,icon:ne[e.value]})))),[]),ve=Object(n.useCallback)((()=>{U(!1),R(null),T(null),me()}),[me]),ge=Object(n.useCallback)((()=>{Q.validateFields().then(l((e=>{r(!0),$===ae.EDIT?y.patch(_(L.id),e).then(l((e=>{b.a.success("\u4fee\u6539\u6210\u529f"),ve();const t=e.data;be(t[se],t),L.parent_id===t.parent_id?O((e=>{const a=((e,t)=>{const a=le(e,t.path);return a&&Object.assign(a,t),e})(e,t);return[...a]})):Oe({search:t.path})}))).finally(l((()=>r(!1)))):y.post(E,e).then(l((e=>{b.a.success("\u65b0\u589e\u6210\u529f"),ve();const t=e.data;t.isLeaf=!0,t.parent_id?$===ae.ADD&&L&&(v.includes(L[se])?O((e=>{const a=((e,t,a)=>{const n=le(e,t);if(!n)return e;n.children?n.children.map((e=>e[se])).includes(a[se])||n.children.unshift(a):n.children=[a];return e})(e,L.path,t);return[...a]})):pe(L)):Oe({depth:2})}))).finally(l((()=>r(!1))))})),l((()=>{b.a.error("\u8bf7\u6b63\u786e\u586b\u5199\u8868\u5355")})))}),[l,Q,L,$,v,ve,pe,Oe,be]);return Object(Y.jsxs)("div",{style:{width:"100%",height:"100%"},children:[Object(Y.jsxs)(u.a,{gutter:10,wrap:!1,children:[Object(Y.jsx)(j.a,{flex:"auto",children:Object(Y.jsx)(p.a.Search,{defaultValue:a,placeholder:"\u8f93\u5165\u8fdb\u884c\u6a21\u7cca\u641c\u7d22",loading:c,onSearch:e=>{ue(e),de===e&&he(je+1)},enterButton:!0})}),Object(Y.jsx)(j.a,{flex:t.tree_manager?"120px":"80px",children:Object(Y.jsxs)(q.a,{children:[Object(Y.jsx)(H.a,{title:"\u52a0\u8f7d\u5168\u90e8\u7ed3\u70b9",children:Object(Y.jsx)(K.a,{type:"primary",icon:Object(Y.jsx)(z.a,{}),onClick:()=>{Oe()}})}),Object(Y.jsx)(H.a,{title:"\u5c55\u5f00/\u6536\u8d77\u5df2\u52a0\u8f7d\u7684\u8282\u70b9",children:Object(Y.jsx)(K.a,{type:"primary",icon:Object(Y.jsx)(P.a,{}),onClick:()=>{g(X?[]:oe(o)),G((e=>!e))}})}),t.tree_manager&&Object(Y.jsx)(H.a,{title:"\u65b0\u589e\u6839\u7ed3\u70b9",children:Object(Y.jsx)(K.a,{type:"primary",icon:Object(Y.jsx)(F.a,{}),onClick:()=>U(!0)})})]})})]}),Object(Y.jsx)("div",{className:"cls-scoll-container cls-tree-view",children:Object(Y.jsx)("div",{className:"cls-scoll-container-wrapper cls-tree-wrapper",children:Object(Y.jsx)("div",{className:"cls-scoll-container-content",children:Object(Y.jsx)(V.a,{tip:"\u52a0\u8f7d\u4e2d",spinning:c,children:Object(Y.jsx)(W.a,{ref:i,treeData:o,fieldNames:{title:"name",key:se},titleRender:e=>Object(Y.jsxs)(q.a,{onMouseEnter:()=>ee(e),onMouseLeave:()=>ee((t=>t[se]===e[se]?null:t)),children:[Object(Y.jsx)("div",{id:`node-${e.path}`,style:xe(e),children:ie(e)}),Object(Y.jsx)(J.a,{menu:{items:fe(e),onClick:t=>{switch(R(t.key),t.key){case ae.REFRESH:pe(e);break;case ae.EDIT:r(!0),y.get(_(e.id)).then(l((t=>{T(e),U(!0),me(t.data)}))).finally(l((()=>r(!1))));break;case ae.ADD:T(e),U(!0),me({parent_id:e.id});break;case ae.DELETE:h.a.warning({title:"\u786e\u8ba4\u5220\u9664\uff1f",content:Object(Y.jsxs)("div",{children:[Object(Y.jsxs)("div",{children:["\u64cd\u4f5c\u5220\u9664\u7ed3\u70b9\uff1a",ie(e)]}),Object(Y.jsxs)("div",{children:["\u7ed3\u70b9\u8def\u5f84: ",e.path]})]}),destroyOnClose:!0,onOk:()=>{y.delete(_(e.id),{params:{path:e.path}}).then(l((()=>{b.a.success(`\u5220\u9664 ${e.path} \u6210\u529f`),O((t=>[...re(t,e)]))})))}})}}},children:Object(Y.jsx)("span",{style:Z&&Z[se]===e[se]?null:{display:"none"},children:Object(Y.jsx)(M.a,{style:{padding:"0 5px"}})})})]}),filterTreeNode:de?e=>de&&e.name.indexOf(de)>-1:void 0,expandedKeys:v,onExpand:(e,t)=>{let{expanded:a,node:n}=t;a&&!S.includes(n[se])?pe(n):g(e)},loadedKeys:S,onLoad:e=>D(e),loadData:e=>new Promise((t=>{pe(e,t)})),multiple:!1,selectedKeys:m?[m]:[],onSelect:(e,t)=>{let{node:a}=t;1===e.length?be(e[0],a):be(null,null)}})})})})}),Object(Y.jsx)(h.a,{title:ae.has($)?ae.getLabel($):"\u65b0\u589e\u7ed3\u70b9",...N,confirmLoading:c,open:A,onOk:()=>ge(),onCancel:()=>ve(),children:Object(Y.jsxs)(d.a,{form:Q,...I,children:[Object(Y.jsx)(d.a.Item,{name:"name",label:"\u6807\u8bc6",rules:[{required:!0,pattern:/^[a-z]([a-z0-9_-]){0,62}[a-z0-9]$/,message:"\u7531\u5c0f\u5199\u5b57\u6bcd\u3001\u6570\u5b57\u3001\u4e2d\u6a2a\u7ebf\u3001\u4e0b\u5212\u7ebf\u7ec4\u6210\uff0c\u5b57\u6bcd\u5f00\u5934\u3001\u5b57\u6bcd\u6216\u6570\u636e\u7ed3\u5c3e\uff0c\u957f\u5ea6\u8303\u56f4\u4e3a2~64"}],children:Object(Y.jsx)(p.a,{disabled:$===ae.EDIT,count:{show:!0,max:64}})}),Object(Y.jsx)(d.a.Item,{name:"alias",label:"\u522b\u540d",rules:[{max:64,message:"\u6700\u591a64\u4e2a\u5b57\u7b26"}],children:Object(Y.jsx)(p.a,{count:{show:!0,max:64}})}),Object(Y.jsx)(d.a.Item,{name:"description",label:"\u63cf\u8ff0",rules:[{max:1024,message:"\u6700\u591a1024\u4e2a\u5b57\u7b26"}],children:Object(Y.jsx)(p.a.TextArea,{autoSize:{minRows:3,maxRows:6},count:{show:!0,max:1024}})}),Object(Y.jsx)(d.a.Item,{name:"parent_id",label:"\u7236\u7ed3\u70b9",help:"\u65e0\u7236\u7c7b\u7ed3\u70b9\u5219\u65b0\u589e\u7684\u662f\u6839\u7ed3\u70b9\uff0c\u66f4\u6539\u5219\u4f1a\u5f71\u54cd\u5176\u6240\u6709\u5b50\u7ed3\u70b9",children:Object(Y.jsx)(te,{disabled:$===ae.ADD,restful:E,fieldNames:{label:"path",value:"id"}})}),Object(Y.jsx)(d.a.Item,{name:"is_key",label:"\u4f5c\u4e3aKey",valuePropName:"checked",children:Object(Y.jsx)(B.a,{disabled:$===ae.EDIT,children:"\u52fe\u9009\u540e\u8be5\u7ed3\u70b9\u4e0d\u5141\u8bb8\u65b0\u589e\u53f6\u5b50\u7ed3\u70b9\uff0c\u4e14\u6807\u8bc6\u4e5f\u662f\u5168\u5c40\u552f\u4e00"})})]})})]})},ue=a(255),je=a(240),he=a(237),be=a(251),pe=a(252),Oe=a(253),me=a(254),xe=a(232),fe=a(241),ve=a(245),ge=a(242);const ye=new Q([{key:"ROLE",value:"role",label:"\u7f16\u89e3\u89d2\u8272"},{key:"ADD_USER",value:"add_user",label:"\u65b0\u589e\u5173\u8054\u7528\u6237"},{key:"DEL_USER",value:"del_user",label:"\u5220\u9664\u5173\u8054\u7528\u6237"}]),ke=e=>{let{isEdit:t=!1}=e;return Object(Y.jsxs)(Y.Fragment,{children:[Object(Y.jsx)(d.a.Item,{name:"name",label:"\u6807\u8bc6",rules:[{required:!0,pattern:/^[a-z]([a-z0-9_-]){0,62}[a-z0-9]$/,message:"\u7531\u5c0f\u5199\u5b57\u6bcd\u3001\u6570\u5b57\u3001\u4e2d\u6a2a\u7ebf\u3001\u4e0b\u5212\u7ebf\u7ec4\u6210\uff0c\u5b57\u6bcd\u5f00\u5934\u3001\u5b57\u6bcd\u6216\u6570\u636e\u7ed3\u5c3e\uff0c\u957f\u5ea6\u8303\u56f4\u4e3a2~64"}],children:Object(Y.jsx)(p.a,{disabled:t,count:{show:!0,max:64}})}),Object(Y.jsx)(d.a.Item,{name:"alias",label:"\u522b\u540d",rules:[{max:64,message:"\u6700\u591a64\u4e2a\u5b57\u7b26"}],children:Object(Y.jsx)(p.a,{count:{show:!0,max:64}})}),Object(Y.jsx)(d.a.Item,{name:"description",label:"\u63cf\u8ff0",rules:[{max:1024,message:"\u6700\u591a1024\u4e2a\u5b57\u7b26"}],children:Object(Y.jsx)(p.a.TextArea,{autoSize:{minRows:3,maxRows:6},count:{show:!0,max:1024}})}),Object(Y.jsx)(d.a.Item,{name:"can_manage",label:"\u5141\u8bb8\u7ba1\u7406\u7ed3\u70b9",valuePropName:"checked",children:Object(Y.jsx)(B.a,{children:"\u52fe\u9009\u540e\uff0c\u8be5\u89d2\u8272\u4e0b\u7684\u6240\u6709\u6210\u5458\u53ef\u5bf9\u7ed3\u70b9\u8fdb\u884c\u7ba1\u7406\uff0c\u5305\u62ec\u5220\u9664\u64cd\u4f5c"})})]})},Se=e=>e.alias?`${e.name} (${e.alias})`:e.name,Ee=e=>{let t=e.username;return(e.first_name||e.last_name)&&(t=`${t}(${e.first_name}${e.last_name})`),t};var _e=e=>{var t;let{user:a,role:s,node:l,onRoleDelete:c}=e;const[r]=f(),[i,o]=Object(n.useState)(!1),[p,O]=Object(n.useState)({...s}),[m,x]=Object(n.useState)(),[v]=d.a.useForm(),[g]=d.a.useForm(),k=Object(n.useCallback)((function(){let e=arguments.length>0&&void 0!==arguments[0]&&arguments[0];s.id&&l.id?(e||void 0===s.user_set)&&(o(!0),y.get($(s.id,l.id),{params:{path:l.path,name:s.name}}).then(r((e=>{O(e.data),o(!1)})))):O({})}),[r,s,l]);return Object(n.useEffect)((()=>{k()}),[k]),Object(n.useEffect)((()=>{O(s)}),[s]),Object(Y.jsxs)(V.a,{spinning:i,children:[Object(Y.jsx)(xe.a,{title:Object(Y.jsxs)(u.a,{wrap:!1,children:[Object(Y.jsx)(j.a,{flex:"auto",children:Object(Y.jsxs)("span",{children:[Object(Y.jsx)(H.a,{title:p.description,children:Se(p)}),p.can_manage&&Object(Y.jsx)(H.a,{title:"\u8be5\u89d2\u8272\u7528\u6237\u53ef\u4ee5\u7ba1\u7406\u7ed3\u70b9",children:Object(Y.jsx)(be.a,{style:{color:"green",marginLeft:5}})})]})}),Object(Y.jsx)(j.a,{flex:a.tree_manager?"120px":a.node_manager?"60px":"0px",children:Object(Y.jsxs)(q.a,{size:"small",children:[(a.tree_manager||a.node_manager)&&Object(Y.jsxs)(Y.Fragment,{children:[Object(Y.jsx)(K.a,{size:"small",icon:Object(Y.jsx)(pe.a,{}),onClick:()=>x(ye.ADD_USER)}),Object(Y.jsx)(H.a,{title:"\u70b9\u51fb\u540e\u53ef\u64cd\u4f5c\u5220\u9664\u5173\u8054\u7528\u6237",children:Object(Y.jsx)(K.a,{size:"small",icon:Object(Y.jsx)(Oe.a,{}),style:m===ye.DEL_USER?{color:"red"}:null,onClick:()=>x(m?null:ye.DEL_USER)})})]}),a.tree_manager&&Object(Y.jsxs)(Y.Fragment,{children:[Object(Y.jsx)(K.a,{size:"small",icon:Object(Y.jsx)(me.a,{}),onClick:()=>{x(ye.ROLE),v.setFieldsValue(p)}}),Object(Y.jsx)(fe.a,{title:"\u786e\u8ba4\u5220\u9664",description:`\u64cd\u4f5c\u5220\u9664\u89d2\u8272 ${p.name} ?`,okText:"\u786e\u8ba4",cancelText:"\u53d6\u6d88",onConfirm:()=>{y.delete($(p.id),{params:{name:p.name}}).then(r((()=>{c&&c(s)})))},children:Object(Y.jsx)(K.a,{size:"small",icon:Object(Y.jsx)(U.a,{}),style:{color:"red"},onClick:()=>x(m?null:ye.DEL_USER)})})]})]})})]}),children:Object(Y.jsx)(ve.a,{wrap:!0,gap:5,className:"cls-view-match-parent",children:null===(t=p.user_set)||void 0===t?void 0:t.map((e=>Object(Y.jsx)(ge.a,{color:e.node_id===l.id?"blue":null,closeIcon:m===ye.DEL_USER&&e.node_id===l.id,onClose:t=>{var a;t.preventDefault(),y.delete(L(e.id),{params:{username:null===(a=e.user)||void 0===a?void 0:a.username,path:l.path,name:p.name}}).then(r((()=>{O((t=>({...t,user_set:t.user_set.filter((t=>t.id!==e.id))})))})))},children:e.node_id===l.id?Ee(e.user):Object(Y.jsx)(H.a,{title:`\u7ee7\u627f\u81ea: ${e.node.path}`,color:"#fff",overlayInnerStyle:{color:"#000",whiteSpace:"nowrap"},children:Ee(e.user)})},e.id)))})}),Object(Y.jsx)(h.a,{title:"\u7f16\u8f91\u89d2\u8272",...N,confirmLoading:i,open:m===ye.ROLE,onOk:()=>{v.validateFields().then(r((e=>{o(!0),y.patch($(p.id),e,{params:{name:p.name,path:l.path}}).then(r((e=>{b.a.success("\u4fee\u6539\u6210\u529f"),x(null),O((t=>({user_set:t.user_set,...e.data})))}))).finally(r((()=>o(!1))))})))},onCancel:()=>x(null),children:Object(Y.jsx)(d.a,{form:v,...I,children:Object(Y.jsx)(ke,{isEdit:!0})})}),Object(Y.jsx)(h.a,{title:"\u65b0\u589e\u5173\u8054\u7528\u6237",...N,confirmLoading:i,open:m===ye.ADD_USER,onOk:()=>{g.validateFields().then(r((e=>{o(!0),y.post(R,{...e,node_id:l.id,role_id:p.id},{params:{path:l.path,role_name:p.name}}).then(r((()=>{b.a.success("\u5173\u8054\u6210\u529f"),x(null),k(!0)}))).finally(r((()=>o(!1))))})))},onCancel:()=>x(null),children:Object(Y.jsx)(d.a,{form:g,...I,children:Object(Y.jsx)(d.a.Item,{name:"user_ids",label:"\u7528\u6237",rules:[{required:!0}],children:Object(Y.jsx)(te,{mode:"multiple",restful:T,fieldNames:{value:"id",label:"username"},antdSelectProps:{style:{width:"100%"},optionRender:e=>Ee(e.data)}})})})})]})};async function we(e){try{await navigator.clipboard.writeText(e),b.a.success(`\u6210\u529f\u62f7\u8d1d: ${e}`)}catch(t){console.error("Failed to copy text: ",t)}}const Ce=Object(n.forwardRef)(((e,t)=>{let{user:a,path:s}=e;const[l]=f(),[c,r]=Object(n.useState)(!1),[i,o]=Object(n.useState)({}),[O,m]=Object(n.useState)(!1),[x,v]=Object(n.useState)({page:1,page_size:20,search:""}),[g,k]=Object(n.useState)({}),[S]=d.a.useForm(),[E,w]=Object(n.useState)(!1),C=Object(n.useCallback)((e=>{e?(r(!0),y.get(_(e)).then(l((e=>{o(e.data),r(!1)})),l((e=>{var t;if(404===(null===(t=e.response)||void 0===t?void 0:t.status)){const e=window.location;window.location.href=`${e.pathname}${e.hash}`}})))):o({})}),[l]),$=Object(n.useCallback)((()=>{m(!0),y.get(D,{params:{...x}}).then(l((e=>{k(e.data),m(!1)})))}),[l,x]);Object(n.useEffect)((()=>{v((e=>({...e,path:s,page:1,search:""})))}),[s]),Object(n.useImperativeHandle)(t,(()=>({fetchNodeDetail:C})),[C]),Object(n.useEffect)((()=>{C(s)}),[s,C]),Object(n.useEffect)((()=>{$()}),[]),Object(n.useEffect)((()=>{$()}),[s,$]);const R=Object(n.useCallback)((()=>{w(!1),S.resetFields()}),[S]),L=Object(n.useMemo)((()=>[{key:"name",label:"\u6807\u8bc6",children:Object(Y.jsxs)("span",{children:[i.name,Object(Y.jsx)(ue.a,{style:{marginLeft:5},onClick:()=>we(i.name)})]})},{key:"alias",label:"\u522b\u540d",children:i.alias},{key:"at",label:"\u65f6\u95f4",children:Object(Y.jsxs)("div",{children:[Object(Y.jsxs)("div",{children:["\u521b\u5efa\uff1a",i.created_at]}),Object(Y.jsxs)("div",{children:["\u66f4\u65b0\uff1a",i.updated_at]})]})},{key:"is_key",label:"\u662f\u5426Key",children:i.is_key?"\u662f":"\u5426"},{key:"path",label:"\u8def\u5f84",span:2,children:Object(Y.jsxs)("span",{children:[i.path,Object(Y.jsx)(ue.a,{style:{marginLeft:5},onClick:()=>we(i.path)})]})},{key:"description",label:"\u63cf\u8ff0",span:3,children:i.description}]),[i]);return i.id?Object(Y.jsxs)("div",{className:"cls-scoll-container",children:[Object(Y.jsx)("div",{className:"cls-scoll-container-wrapper",children:Object(Y.jsxs)("div",{className:"cls-scoll-container-content",children:[Object(Y.jsx)(V.a,{spinning:c,children:Object(Y.jsx)(je.a,{title:Object(Y.jsx)("div",{className:"cls-common-title",children:"\u57fa\u672c\u4fe1\u606f"}),bordered:!0,column:{xs:1,md:2,xl:3},items:L})}),Object(Y.jsx)(V.a,{spinning:O,children:Object(Y.jsx)(he.a,{className:"cls-role-list-view",header:Object(Y.jsxs)(u.a,{wrap:!1,children:[Object(Y.jsx)(j.a,{flex:"auto",children:Object(Y.jsx)("div",{className:"cls-common-title",children:"\u89d2\u8272\u6210\u5458"})}),Object(Y.jsx)(j.a,{flex:a.tree_manager?"350px":"250px",children:Object(Y.jsxs)(q.a,{children:[Object(Y.jsx)(p.a.Search,{style:{width:250},placeholder:"\u8f93\u5165\u89d2\u8272\u8fdb\u884c\u641c\u7d22",loading:O,onSearch:e=>v((t=>({...t,search:e}))),enterButton:!0}),a.tree_manager&&Object(Y.jsx)(K.a,{type:"primary",onClick:()=>w(!0),children:"\u65b0\u589e\u89d2\u8272"})]})})]}),grid:{gutter:10,xs:1,md:2,xl:2},dataSource:g.results,loading:O,renderItem:e=>Object(Y.jsx)(he.a.Item,{children:Object(Y.jsx)(_e,{user:a,role:e,node:i,onRoleDelete:e=>{k((t=>({count:t.count-1,results:t.results.filter((t=>t.id!==e.id))})))}})}),pagination:{size:"small",total:g.count,showTotal:e=>`\u603b\u8ba1: ${e}`,current:x.page,pageSize:x.page_size,showSizeChanger:!0,pageSizeOptions:[50,100,500,1e3],showQuickJumper:!0,onChange:(e,t)=>v((a=>({...a,page:e,page_size:t})))}})})]})}),Object(Y.jsx)(h.a,{title:"\u65b0\u589e\u89d2\u8272",...N,confirmLoading:O,open:E,onOk:()=>{S.validateFields().then(l((e=>{m(!0),y.post(D,e,{params:{name:e.name}}).then(l((()=>{b.a.success("\u65b0\u589e\u89d2\u8272\u6210\u529f"),R(),$()}))).finally(l((()=>m(!1))))})))},onCancel:()=>R(),children:Object(Y.jsx)(d.a,{form:S,...I,children:Object(Y.jsx)(ke,{})})})]}):Object(Y.jsx)("div",{children:"\u8bf7\u70b9\u51fb\u9009\u62e9\u7ed3\u70b9"})}));Ce.displayName="NodeView";var De=Ce;var $e=function(){var e;const[t,a]=Object(n.useState)(null===(e=m.a.parse(window.location.search))||void 0===e?void 0:e.path),s=Object(n.useRef)(),[l]=f(),[c,r]=Object(n.useState)(!1),[i,o]=Object(n.useState)({}),[O,x]=Object(n.useState)(!1),[v]=d.a.useForm(),g=Object(n.useCallback)((()=>{r(!0),y.get(S,{params:{path:t}}).then(l((e=>{o(e.data.user)})),l((e=>{var t;401===(null===e||void 0===e||null===(t=e.response)||void 0===t?void 0:t.status)&&x(!0)}))).finally(l((()=>r(!1))))}),[t,l]);return Object(n.useEffect)((()=>{g()}),[g,t]),Object(Y.jsxs)("div",{className:"cls-view-match-parent",children:[Object(Y.jsxs)(u.a,{style:{height:"100%",padding:10},gutter:20,children:[Object(Y.jsx)(j.a,{span:6,children:Object(Y.jsx)(de,{user:i,defaultValue:t,onChange:e=>{let{path:n}=e;var l;t===n?null===(l=s.current)||void 0===l||l.fetchNodeDetail(n):a(n);const c=window.location;let r=`${c.pathname}${c.hash}`;n&&n.indexOf(k)>-1&&(r=`${r}?path=${n}`),history.pushState(null,null,r)}})}),Object(Y.jsx)(j.a,{span:18,children:Object(Y.jsx)(De,{ref:s,user:i,path:t})})]}),Object(Y.jsx)(h.a,{title:"\u65b0\u589e\u89d2\u8272",confirmLoading:c,open:O,onOk:()=>{v.validateFields().then(l((e=>{r(!0),y.post(S,e).then(l((()=>{b.a.success("\u767b\u5f55\u6210\u529f"),x(!1),location.reload()}))).finally(l((()=>r(!1))))})))},onCancel:()=>x(!1),children:Object(Y.jsxs)(d.a,{form:v,...I,children:[Object(Y.jsx)(d.a.Item,{name:"username",label:"\u7528\u6237\u540d",rules:[{required:!0}],children:Object(Y.jsx)(p.a,{})}),Object(Y.jsx)(d.a.Item,{name:"password",label:"\u5bc6\u7801",rules:[{required:!0}],children:Object(Y.jsx)(p.a.Password,{})})]})})]})};o.a.createRoot(document.getElementById("root")).render(Object(Y.jsx)(s.a.StrictMode,{children:Object(Y.jsx)(r.a,{locale:c.a,children:Object(Y.jsx)($e,{})})}))}},[[218,1,2]]]);
//# sourceMappingURL=main.e4384f09.chunk.js.map
