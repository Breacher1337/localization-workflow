package com.applicationjp;

import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;
import javassist.*;

public class AgentMain {
    public static void premain(String agentArgs, Instrumentation inst) {
        inst.addTransformer(new ClassFileTransformer() {
            @Override
            public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
                                    ProtectionDomain protectionDomain, byte[] classfileBuffer) {
                if (className == null) return null;

                // Target UI rendering classes
                if (className.startsWith("com/fs/legacyapp/ui/") ||
                    className.equals("com/fs/legacyapp/api/util/Misc") ||
                    className.equals("com/fs/legacyapp/api/impl/campaign/intel/MessageIntel")) {

                    try {
                        ClassPool cp = ClassPool.getDefault();
                        CtClass cc = cp.makeClass(new java.io.ByteArrayInputStream(classfileBuffer));
                        boolean pluginified = false;

                        for (CtMethod method : cc.getDeclaredMethods()) {
                            // Intercept setText, addPara, addParagraph, etc.
                            if (method.getName().equals("setText") ||
                                method.getName().equals("addPara") ||
                                method.getName().equals("addParagraph")) {

                                try {
                                    CtClass[] params = method.getParameterTypes();
                                    if (params.length > 0 && params[0].getName().equals("java.lang.String")) {
                                        method.insertBefore("{  = com.applicationjp.JPTranslationPlugin.translate(); }");
                                        pluginified = true;
                                    }
                                } catch (NotFoundException e) {}
                            }
                        }

                        if (pluginified) {
                            byte[] bytecode = cc.toBytecode();
                            cc.detach();
                            return bytecode;
                        }
                    } catch (Exception e) {
                        // In an agent, we must be careful not to throw exceptions back to the JVM
                        // as it might crash the boot sequence.
                    }
                }
                return null;
            }
        });
    }
}
