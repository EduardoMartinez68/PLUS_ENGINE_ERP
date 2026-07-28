function convert_path_global_functions(ruta) {
    return ruta
        // Remove the trailing extension (e.g., .html) if it has one.
        .replace(/\.[^/.]+$/, "")

        // Replace backslashes (\) and slashes (/) with underscores (_)
        .replace(/[\\/]+/g, "_");
}

// create the variable global <AppFunctions> if not exist and create the object
window.Plus = window.Plus || {};
Plus.Functions = {
    modules: {},
    /**
     * @param {string} namespace
     * The unique namespace that identifies the JavaScript file.
     * Usually generated from the file path inside the ERP, for example:
     * "apps_customers_views_form".
     *
     * @param {string} name
     * The name used to register the function inside the namespace.
     * This name is later used to retrieve and execute the function.
     *
     * @param {Function} fn
     * The function to register in the global registry.
     */

    //in this function we will to save the function of the script 
    //use the <id> global of plus that was create in the backend
    define(namespace, name, fn) {
        namespace=convert_path_global_functions(namespace)
        if (!this.modules[namespace]) {
            this.modules[namespace] = {};
        }
        this.modules[namespace][name] = fn;
    },

    //in this function are get a function in specific use the namespace
    get(namespace) {
        namespace=convert_path_global_functions(namespace)
        if (this.modules[namespace]) {
            return this.modules[namespace];
        }

        console.warn(`Module '${namespace}' not found.`);
        return {};
    },

    executeWithAfter(namespace, mainFnName, afterFnName = null, ...args) {
        namespace = convert_path_global_functions(namespace);

        if (this.modules[namespace] && typeof this.modules[namespace][mainFnName] === 'function') {
            
            // Ejecuta la función principal
            const result = this.modules[namespace][mainFnName](...args);

            // Helper interno para ejecutar la función secundaria si existe
            const runAfter = () => {
                if (afterFnName && typeof this.modules[namespace][afterFnName] === 'function') {
                    this.modules[namespace][afterFnName]();
                }
            };

            // Si devuelve una promesa (Fetch / AJAX)
            if (result && typeof result.then === 'function') {
                return result.then((res) => {
                    runAfter();
                    return res;
                });
            }

            // Si es síncrona
            runAfter();
            return result;
        }

        console.warn(`Function '${mainFnName}' in module '${namespace}' not found.`);
        return null;
    },

    /**
     * Ejecuta una secuencia ordenada de funciones dentro de un mismo namespace.
     * @param {string} namespace - El modulo donde residen las funciones.
     * @param {Array<string>} fnNames - Lista ordenada de nombres de funciones a ejecutar.
     * @param {...*} initialArgs - Argumentos iniciales para la primera función.
     */
    async pipe(namespace, fnNames, ...initialArgs) {
        namespace = convert_path_global_functions(namespace);
        
        const module = this.modules[namespace];
        if (!module) {
            console.warn(`Module '${namespace}' not found.`);
            return null;
        }

        let currentResult = initialArgs;

        for (const name of fnNames) {
            if (typeof module[name] !== 'function') {
                console.warn(`Function '${name}' in module '${namespace}' not found. Stopping pipeline.`);
                break;
            }

            // Normalizamos los argumentos: la 1ra recibe initialArgs, las siguientes el resultado previo
            const argsToPass = Array.isArray(currentResult) && fnNames.indexOf(name) === 0 
                ? currentResult 
                : [currentResult];

            // 'await' asegura que si la función devuelve una Promesa (fetch/AJAX), 
            // la ejecución espere antes de pasar a la siguiente función
            currentResult = await module[name](...argsToPass);
        }

        return currentResult;
    },

     /**
     * Registra un callback que se ejecutará INMEDIATAMENTE DESPUÉS
     * de que la función objetivo termine su ejecución.
     */
    after(namespace, targetFnName, callback) {
        namespace = convert_path_global_functions(namespace);

        // Si el módulo no existe aún, lo creamos
        if (!this.modules[namespace]) {
            this.modules[namespace] = {};
        }

        // Guardamos una referencia a la función original (si ya existe)
        const originalFn = this.modules[namespace][targetFnName];

        // Reemplazamos la función objetivo con un wrapper
        this.modules[namespace][targetFnName] = async function (...args) {
            let result;

            // 1. Ejecutamos la función original (si existe)
            if (typeof originalFn === 'function') {
                result = await originalFn(...args);
            }

            // 2. Ejecutamos el callback pasando la respuesta/resultado de la original
            if (typeof callback === 'function') {
                await callback(result);
            }

            // 3. Retornamos el resultado original por si alguien más lo necesita
            return result;
        };
    },

    /**
    * Deletes functions. If you pass a namespace, deletes only that module.
    * If you don't pass anything, resets the entire function registry.
    */
    reset(namespace = null) {
        if (namespace) {
            namespace = convert_path_global_functions(namespace);
            delete this.modules[namespace];
        } else {
            this.modules = {};
        }
    }
};

Plus.variables = {
    /**
     * Registers a variable reference inside the global PLUS ERP registry.
     *
     * Instead of storing the variable value, this method stores an object
     * reference. This allows the latest value to be retrieved at any time,
     * even if the variable changes after being registered.
     *
     * @param {string} namespace
     * Unique identifier of the JavaScript module.
     *
     * @param {string} variable_name
     * Name used to register the variable inside the module.
     *
     * @param {Object} refObj
     * Object containing the variable reference.
     * Example: { value: myVariable }
     */
    registry: {},

    // Función para registrar una variable por referencia (usando un objeto contenedor)
    define: function(namespace, variable_name, refObj) {
        namespace=convert_path_global_functions(namespace)
        if (!this.registry[namespace]) {
            this.registry[namespace] = {};
        }

        // save the reference complete of the object 
        this.registry[namespace][variable_name] = refObj;
    },

    // Función tercera para obtener el valor actualizado en tiempo real
    get: function(namespace, variable_name) {
        namespace=convert_path_global_functions(namespace)
        if (this.registry[namespace] && this.registry[namespace][variable_name]) {
            // Retorna siempre la propiedad .value actualizada
            return this.registry[namespace][variable_name].value;
        }
        console.warn(`No se encontró la variable '${variable_name}' para la clave '${namespace}'`);
        return null;
    },

    /**
    * Deletes variables. If you pass a namespace, deletes only that module.
    * If you don't pass anything, resets the entire variable registry.
    */
    reset(namespace = null) {
        if (namespace) {
            namespace = convert_path_global_functions(namespace);
            delete this.registry[namespace];
        } else {
            this.registry = {};
        }
    }
};
//  apps\contract\views\home.html



// ---  JS encapsulation ---
(()=>{
    /*
    //this variable is for can render all the container
    //this variable are remplace when the server run and load all the container
    const namespace = "{plus}";
    
    //here your create a function encapsulated
    function render_canva() {
        console.log("¡Ejecutando render_canva desde la clave {plus}!");
    }

    // save the function in the variable globale <AppFunctions> for after use in other scripts 
    window.Plus.Functions.define(namespace, "render", render_canva);
    window.Plus.Functions.get(namespace).create(); //here we run a function in specific
    */
})();
